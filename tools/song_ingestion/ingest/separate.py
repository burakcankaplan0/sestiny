"""Vokal ayrıştırma: tam miksten lead vokal stem'ini ayırır.

Neden şart: pitch analizini tam mikse uygularsak enstrüman frekansları "nota"
sanılır ve sahte aralık üretilir. Önce vokali izole edip pitch'i temiz stem
üzerinde çalıştırırız.

Model seçilebilir (bkz. plan Q3):
- "mel_band_roformer" (varsayılan): en temiz vokal, en az sızıntı. Mac'te
  python-audio-separator + CoreML üzerinden. Ağırlıklar araştırma/NC lisanslı.
- "htdemucs_ft" (yedek): Meta, MIT lisans, sağlam. Mac'te CPU veya MLX.

Mac notu: ham torch MPS bu modellerde güvenilmezdir; CoreML (ONNX) / MLX yolu
tercih edilir.

BU MODÜL FAZ 1'DE DOLDURULACAK. Ağır import'lar fonksiyon içinde yapılacaktır.
"""

from __future__ import annotations

from dataclasses import dataclass

DEFAULT_MODEL = "mel_band_roformer"
FALLBACK_MODEL = "htdemucs_ft"


@dataclass(frozen=True)
class SeparationResult:
    """Ayrıştırma çıktısı: izole vokal + kalıntı sızıntı göstergesi."""

    vocals: object  # np.ndarray (Faz 0'da numpy zorunlu tutulmuyor)
    sample_rate: int
    model: str
    # Ayrıştırma sonrası vokal-dışı enerji tahmini (0-1). Yüksekse pitch'e
    # güven düşürülür — confidence.py bunu kullanır.
    residual_bleed: float


def separate_vocals(samples, sample_rate: int, model: str = DEFAULT_MODEL) -> "SeparationResult":
    """Tam miksten lead vokali ayırır. Faz 1'de doldurulacak."""
    raise NotImplementedError(
        "Vokal ayrıştırma Faz 1'de eklenecek (audio-separator / demucs). "
        "Ağır bağımlılıklar o zaman kurulacak."
    )
