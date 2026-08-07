"""Pitch (F0) çıkarımı — RMVPE (ONNX, torch'suz).

DIRECT pipeline (Faz 1/Adım 2): tam miks doğrudan RMVPE'ye verilir; vokal
ayrıştırma YOK. RMVPE polifonik müzikten vokal F0 çıkarmak için tasarlandığı
için bu bir başlangıç varsayımıdır — ayrıştırmanın gerçekten daha doğru olup
olmadığı ileride benchmark edilecek (Pipeline B), ölçmeden zorunlu kılınmayacak.

Ağır import (`rmvpe_onnx`) yalnızca fonksiyon içinde yapılır; modül, rmvpe-onnx
kurulu olmadan da import edilebilir (motorun geri kalanı sentetik frame'lerle
test edilebilsin diye).

RMVPE.predict(audio, sr) → (times, f0_hz, confidence, salience). İlk üçünü
kullanırız; salience (N×360) bize gerekmez.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..config import RMVPE_SAMPLE_RATE

DEFAULT_MODEL = "rmvpe"

# RMVPE örneği pahalı yüklenir (362 MB model); süreç içinde bir kez tutulur.
_rmvpe_instance = None


@dataclass(frozen=True)
class PitchFrames:
    """Zaman-hizalı F0 dizisi (hepsi eşit uzunlukta numpy dizileri)."""

    times: object  # np.ndarray, saniye
    f0_hz: object  # np.ndarray, Hz (sessiz/güvensiz frame'lerde 0/NaN olabilir)
    confidence: object  # np.ndarray, frame başına 0-1
    model: str


def _get_rmvpe():
    global _rmvpe_instance
    if _rmvpe_instance is None:
        from rmvpe_onnx import RMVPE  # lazy: ağır bağımlılık

        _rmvpe_instance = RMVPE()
    return _rmvpe_instance


def extract_f0(audio, sample_rate: int, model: str = DEFAULT_MODEL) -> PitchFrames:
    """Ses dizisinden zaman-içi F0 + frame güveni çıkarır (Direct RMVPE).

    audio: mono float32 numpy dizisi. sample_rate 16 kHz değilse yeniden
    örneklenir (RMVPE 16 kHz bekler).
    """
    import numpy as np

    audio = np.asarray(audio, dtype=np.float32)
    if sample_rate != RMVPE_SAMPLE_RATE:
        import librosa

        audio = librosa.resample(audio, orig_sr=sample_rate, target_sr=RMVPE_SAMPLE_RATE)

    rmvpe = _get_rmvpe()
    times, f0_hz, confidence, _salience = rmvpe.predict(audio, RMVPE_SAMPLE_RATE)

    return PitchFrames(
        times=np.asarray(times, dtype=np.float64),
        f0_hz=np.asarray(f0_hz, dtype=np.float64),
        confidence=np.asarray(confidence, dtype=np.float64),
        model="rmvpe_direct",
    )
