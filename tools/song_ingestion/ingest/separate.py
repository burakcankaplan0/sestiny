"""Vokal ayrıştırma — tam miksten "vocals stem" üretir (Pipeline B benchmark).

ÖNEMLİ (mimari düzeltme, kullanıcı): standart bir separator otomatik olarak
"yalnızca lead vocal" ÜRETMEZ. Enstrüman leakage'ını büyük ölçüde temizler ama
backing/harmony vokalleri vocals stem içinde bırakabilir. Bu yüzden çıktı
bilinçli olarak "vocals stem" diye adlandırılır, "lead vocal" değil. Bu aşamanın
amacı yalnızca: "Direct RMVPE'deki yanlış uçlar standart vocal separation ile
düzeliyor mu?" sorusunu ölçmek.

Model: **htdemucs** (standart), demucs-mlx üzerinden. **Hazır MLX ağırlıkları**
kullanılır — PyTorch GEREKMEZ, yerel checkpoint dönüştürme YOK, [convert] extra
YOK (mlx-audio-separator'ın RoFormer modelleri torch dönüştürme istediği için
o yoldan vazgeçildi; bkz. K-071). Ağır import fonksiyon içinde.

htdemucs 4 stem üretir: vocals / drums / bass / other. Biz vocals'ı alırız.

Ayrıştırma pahalı → stem, dosya içeriği hash'iyle cache edilir; aynı dosya iki
kez ayrılmaz. Cache Git'e ve production'a girmez (gitignore).
"""

from __future__ import annotations

from pathlib import Path

# Standart htdemucs (hazır MLX). htdemucs_ft/büyük modeller şimdilik kullanılmaz.
SEPARATION_MODEL = "htdemucs"

# Hazır ön-dönüştürülmüş MLX ağırlıklarının kaynağı (torch GEREKTİRMEZ).
# demucs-mlx varsayılan olarak PyTorch ağırlıklarını yerelde dönüştürmeye
# çalışıyor ([convert]/torch ister); bunun yerine bu HF deposundaki hazır MLX
# safetensors indirilip demucs-mlx cache dizinine konur, böylece
# load_mlx_model onları doğrudan (safetensors.mlx ile) yükler (bkz. K-071).
MLX_WEIGHTS_REPO = "mlx-community/demucs-mlx"

_separator_cache: dict = {}


def _ensure_mlx_weights(model: str) -> None:
    """Hazır MLX safetensors + config'i (yoksa) HF'ten demucs-mlx cache'ine indirir."""
    from demucs_mlx.model_converter import get_mlx_cache_dir
    from huggingface_hub import hf_hub_download

    cache_dir = Path(get_mlx_cache_dir())
    cache_dir.mkdir(parents=True, exist_ok=True)
    for filename in (f"{model}.safetensors", f"{model}_config.json"):
        if not (cache_dir / filename).exists():
            hf_hub_download(
                repo_id=MLX_WEIGHTS_REPO,
                filename=filename,
                local_dir=str(cache_dir),
            )


# htdemucs model varsayılanları (mlx_htdemucs.py); hazır config bunları None
# bıraktığı için elle geri konur (bkz. aşağıdaki workaround).
_HTDEMUCS_SAMPLERATE = 44100
_HTDEMUCS_SEGMENT = 10


def _get_separator(model: str):
    if model not in _separator_cache:
        _ensure_mlx_weights(model)  # torch'suz, hazır MLX ağırlıkları
        from demucs_mlx import Separator  # lazy: MLX, torch YOK

        # WORKAROUND (bkz. K-071): demucs-mlx 1.4.4, mlx-community hazır config'inde
        # segment/samplerate None geldiği için iç modele bozuk bir değer atıyor ve
        # valid_length'te int() patlıyor. split=False (128 GB RAM'de tam parça bir
        # kerede işlenir, chunk sınırı artefaktı da olmaz) + iç modellere model
        # varsayılanlarını elle koymak sorunu çözüyor.
        separator = Separator(model=model, progress=False, split=False)
        for sub_model in getattr(separator._model, "models", []) or []:
            if hasattr(sub_model, "segment"):
                sub_model.segment = _HTDEMUCS_SEGMENT
            if hasattr(sub_model, "samplerate"):
                sub_model.samplerate = _HTDEMUCS_SAMPLERATE
            if hasattr(sub_model, "use_train_segment"):
                sub_model.use_train_segment = False
        _separator_cache[model] = separator
    return _separator_cache[model]


def separate_vocals_stem(
    audio_path: str | Path,
    cache_dir: str | Path,
    content_hash: str,
    model: str = SEPARATION_MODEL,
) -> Path:
    """Tam miksten vocals stem üretir ve cache'ler; stem dosyasının yolunu döner.

    content_hash aynıysa yeniden ayrıştırma yapılmaz (pahalı işlemin cache'i).
    """
    import numpy as np
    import soundfile as sf

    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    stem_path = cache_dir / f"{content_hash}__vocals__{model}.wav"
    if stem_path.exists():
        return stem_path

    separator = _get_separator(model)
    _origin, stems = separator.separate_audio_file(str(audio_path))
    if "vocals" not in stems:
        raise RuntimeError(f"Ayrıştırma vocals stem üretmedi; stem'ler: {list(stems)}")

    vocals = np.asarray(stems["vocals"], dtype=np.float32)
    # demucs stem'i (kanal, örnek) düzeninde; soundfile (örnek, kanal) bekler.
    if vocals.ndim == 2 and vocals.shape[0] < vocals.shape[1]:
        vocals = vocals.T
    sf.write(str(stem_path), vocals, int(separator.samplerate))
    return stem_path
