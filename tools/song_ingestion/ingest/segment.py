"""Sung / rap / spoken segment sınıflaması — sahte aralık üretimini önler.

Yöntem (bkz. plan Q3-bis): şarkı = yüksek ve belirgin şekilde STABİL F0.
Segment başına ölçülür: voiced oran, F0'ın ~±50 cent içinde ≥ min süre tutulan
frame oranı (sürekli-nota oranı), kısa-vadeli F0 varyansı. Rap/konuşma → düşük
sürekli-nota oranı + yüksek varyans.

Öğrenilmiş model yerine bilinçli olarak şeffaf sezgisel kullanılır (kırılganlık
düşük, "neden böyle sınıfladı" açıklanabilir).

Track düzeyinde vocal_mode kararı:
- yeterli sürekli-nota → "sung"
- kısmi (bazı melodik bölümler) → "melodic_rap" / "mixed"
- neredeyse hiç sürekli-nota → "rap": ARALIK ÜRETİLMEZ, review'a düşer.

BU MODÜL FAZ 1'DE DOLDURULACAK.
"""

from __future__ import annotations

from dataclasses import dataclass

# Bir frame kümesinin "sürekli nota" sayılması için gereken en az süre.
MIN_SUSTAINED_NOTE_MS = 120
# Bir notanın "stabil" sayılması için F0'ın kalması gereken bant (± cent).
STABLE_NOTE_TOLERANCE_CENTS = 50


@dataclass(frozen=True)
class VocalModeResult:
    vocal_mode: str  # sung / melodic_rap / rap / mixed
    sustained_note_ratio: float  # 0-1, ne kadarı sürekli melodik nota
    has_reliable_melodic_range: bool  # False ise aralık üretilmez


def classify_vocal_mode(pitch_frames, sample_rate: int) -> "VocalModeResult":
    """F0 stabilitesinden sung/rap ayrımı yapar. Faz 1'de doldurulacak."""
    raise NotImplementedError("Sung/rap sınıflaması Faz 1'de eklenecek.")
