"""Full vocal range + tessitura — nota segmentlerinden hesaplanır.

- Full range: yalnızca UÇ-nota eşiğini (daha katı süre/frame) geçen
  segmentlerden en pes ve en tiz. Kısa/tekil bir yüksek geçiş ucu belirlemez.
  Uç notaların timestamp'i ve süresi kaydedilir (review'da "o anı dinle" için).
- Tessitura: kabul edilen tüm segmentlerin SÜRE-AĞIRLIKLI dağılımından, toplam
  vokal süresinin ~%TESSITURA_COVERAGE'ını kaplayan en dar sürekli MIDI bandı.
  Tek kullanımlık ad-lib tessitura'yı genişletmez.

Yalnızca numpy — sentetik segmentlerle test edilebilir.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..config import (
    EXTREME_MIN_DURATION_SECONDS,
    EXTREME_MIN_SUPPORTING_FRAMES,
    TESSITURA_COVERAGE,
)
from ..notes import midi_to_note_name
from .note_segments import NoteSegment


@dataclass(frozen=True)
class RangeResult:
    full_range_low_midi: int
    full_range_high_midi: int
    full_range_low_note: str
    full_range_high_note: str
    range_semitones: int
    low_note_timestamp: float
    high_note_timestamp: float
    low_note_duration: float
    high_note_duration: float
    tessitura_low_midi: int
    tessitura_high_midi: int
    tessitura_low_note: str
    tessitura_high_note: str


def _tessitura(segments: list[NoteSegment]) -> tuple[int, int]:
    """Süre-ağırlıklı en dar sürekli MIDI bandı (kapsama ≥ TESSITURA_COVERAGE).

    Yöntem: her yarım ton için toplam süre (histogram) çıkarılır; ardından
    en pesten en tize sürekli pencereler taranıp toplam sürenin
    TESSITURA_COVERAGE oranını karşılayan EN DAR pencere seçilir.
    """
    durations: dict[int, float] = {}
    for seg in segments:
        durations[seg.midi] = durations.get(seg.midi, 0.0) + seg.duration
    total = sum(durations.values())
    if total <= 0:
        raise ValueError("Tessitura için süre yok.")

    lo_midi = min(durations)
    hi_midi = max(durations)
    target = TESSITURA_COVERAGE * total

    best_low, best_high = lo_midi, hi_midi
    best_span = hi_midi - lo_midi
    for low in range(lo_midi, hi_midi + 1):
        covered = 0.0
        for high in range(low, hi_midi + 1):
            covered += durations.get(high, 0.0)
            if covered >= target:
                span = high - low
                if span < best_span:
                    best_span = span
                    best_low, best_high = low, high
                break  # bu low için en dar pencere bulundu
    return best_low, best_high


def compute_range(segments: list[NoteSegment]) -> RangeResult | None:
    """Segmentlerden full range + tessitura. Uç-nota eşiğini geçen segment
    yoksa None döner (aralık uydurulmaz)."""
    if not segments:
        return None

    eligible = [
        seg
        for seg in segments
        if seg.duration >= EXTREME_MIN_DURATION_SECONDS
        and seg.frame_count >= EXTREME_MIN_SUPPORTING_FRAMES
    ]
    if not eligible:
        return None

    low_seg = min(eligible, key=lambda s: s.midi)
    high_seg = max(eligible, key=lambda s: s.midi)

    tess_low, tess_high = _tessitura(segments)

    return RangeResult(
        full_range_low_midi=low_seg.midi,
        full_range_high_midi=high_seg.midi,
        full_range_low_note=midi_to_note_name(low_seg.midi),
        full_range_high_note=midi_to_note_name(high_seg.midi),
        range_semitones=high_seg.midi - low_seg.midi,
        low_note_timestamp=low_seg.start_time,
        high_note_timestamp=high_seg.start_time,
        low_note_duration=low_seg.duration,
        high_note_duration=high_seg.duration,
        tessitura_low_midi=tess_low,
        tessitura_high_midi=tess_high,
        tessitura_low_note=midi_to_note_name(tess_low),
        tessitura_high_note=midi_to_note_name(tess_high),
    )
