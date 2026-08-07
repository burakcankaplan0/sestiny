"""analysis_confidence — ÖLÇÜLEN kaliteden türetilir, sabit sayı DEĞİL.

Kullanıcının katı isteği: "MIDI = 0.9, Audio = 0.7 gibi keyfi güven verme."
Güven, gerçekten ölçülen bileşenlerden üretilir; ağırlıklar ve formül config'te
(CONF_WEIGHT_*), açıklaması docs/ANALYSIS_THRESHOLDS.md'de.

Formül:
    base = W_AVG*avg_conf + W_VOICED*voiced_ratio
         + W_COVERAGE*coverage + W_EXTREME*extreme_support
    confidence = base * (1 - JUMP_PENALTY * octave_jump_ratio)   → [0,1]
"""

from __future__ import annotations

from ..config import (
    CONF_JUMP_PENALTY,
    CONF_WEIGHT_AVG_CONFIDENCE,
    CONF_WEIGHT_EXTREME_SUPPORT,
    CONF_WEIGHT_SEGMENT_COVERAGE,
    CONF_WEIGHT_VOICED_RATIO,
    EXTREME_MIN_DURATION_SECONDS,
)


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def compute_confidence(
    *,
    average_pitch_confidence: float,
    voiced_frame_ratio: float,
    segment_coverage: float,
    low_note_duration: float,
    high_note_duration: float,
    octave_jump_ratio: float,
) -> float:
    """Ölçülen bileşenlerden 0-1 güven üretir.

    - average_pitch_confidence: kabul edilen frame'lerin ortalama RMVPE güveni
    - voiced_frame_ratio: geçerli frame / toplam frame
    - segment_coverage: geçerli segment süresi / toplam ses süresi
    - low/high_note_duration: uç notaların desteklenme süresi
    - octave_jump_ratio: parçalılık göstergesi (çarpımsal ceza)
    """
    # Uç nota desteği: iki ucun daha zayıf olanı, "yeterince uzun" eşiğine oranlanır.
    extreme_support = _clamp(
        min(low_note_duration, high_note_duration) / EXTREME_MIN_DURATION_SECONDS
    )

    base = (
        CONF_WEIGHT_AVG_CONFIDENCE * _clamp(average_pitch_confidence)
        + CONF_WEIGHT_VOICED_RATIO * _clamp(voiced_frame_ratio)
        + CONF_WEIGHT_SEGMENT_COVERAGE * _clamp(segment_coverage)
        + CONF_WEIGHT_EXTREME_SUPPORT * extreme_support
    )
    penalized = base * (1.0 - CONF_JUMP_PENALTY * _clamp(octave_jump_ratio))
    return round(_clamp(penalized), 3)
