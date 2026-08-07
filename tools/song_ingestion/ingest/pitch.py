"""Pitch (F0) çıkarımı — izole vokalden zaman içindeki temel frekans + güven.

Model seçilebilir (bkz. plan Q4):
- "rmvpe" (varsayılan): eşlik/sızıntı varken bile vokal F0'ı doğru okumak için
  tasarlanmış; frame başına güven verir; ONNX (torch'a girmez).
- "fcpe" / "torchcrepe" (yedek).
- "pyin": yalnızca temiz frame'lerde bağımsız çapraz kontrol.

Çıktı, backend/app/services/pitch_analysis.py'deki PitchTrack ile aynı ruhta:
frame başına f0 + güven; sonra range.py oktav hatası / kısa nota / düşük güven
elemesini uygular (o modülün _remove_pitch_jumps yaklaşımı yeniden kullanılacak).

BU MODÜL FAZ 1'DE DOLDURULACAK.
"""

from __future__ import annotations

from dataclasses import dataclass

DEFAULT_MODEL = "rmvpe"


@dataclass(frozen=True)
class PitchFrames:
    """Zaman-hizalı F0 dizisi."""

    times: object  # np.ndarray, saniye
    f0_hz: object  # np.ndarray, sessiz frame'lerde 0/NaN
    confidence: object  # np.ndarray, frame başına 0-1
    model: str


def extract_f0(vocals, sample_rate: int, model: str = DEFAULT_MODEL) -> "PitchFrames":
    """İzole vokalden zaman-içi F0 + frame güveni. Faz 1'de doldurulacak."""
    raise NotImplementedError(
        "Pitch çıkarımı Faz 1'de eklenecek (rmvpe-onnx varsayılan). "
        "Ağır bağımlılıklar o zaman kurulacak."
    )
