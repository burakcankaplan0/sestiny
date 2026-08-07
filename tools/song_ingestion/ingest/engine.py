"""Direct RMVPE analiz motoru — aşamaları birleştirip tek şarkı sonucu üretir.

pitch (RMVPE) → nota segmentasyonu → full range + tessitura → confidence →
needs_review. Süreler ölçülür. Ayrıntılı debug raporu üretilebilir (yalnızca
lab; production'a gitmez).

analyze_frames() sentetik PitchFrames ile test edilebilir (RMVPE gerekmez).
analyze_audio() gerçek ses için RMVPE'yi çalıştırır.
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field

from ..config import (
    MAX_OCTAVE_JUMP_RATIO,
    MIN_VALID_FRAMES_FOR_RANGE,
    NEEDS_REVIEW_CONFIDENCE,
    SUSPICIOUS_RANGE_SEMITONES,
)
from .confidence import compute_confidence
from .note_segments import NoteSegment, segment_notes
from .range import RangeResult, compute_range

ANALYSIS_VERSION = "direct-rmvpe-0.1"


@dataclass
class AnalysisResult:
    # full range
    full_range_low_note: str | None = None
    full_range_high_note: str | None = None
    full_range_low_midi: int | None = None
    full_range_high_midi: int | None = None
    # tessitura
    tessitura_low_note: str | None = None
    tessitura_high_note: str | None = None
    tessitura_low_midi: int | None = None
    tessitura_high_midi: int | None = None
    range_semitones: int | None = None
    # uç nota timestamp/süre
    low_note_timestamp: float | None = None
    high_note_timestamp: float | None = None
    low_note_duration: float | None = None
    high_note_duration: float | None = None
    # ölçülen kalite
    average_pitch_confidence: float = 0.0
    voiced_frame_ratio: float = 0.0
    discarded_frame_ratio: float = 1.0
    octave_jump_ratio: float = 0.0
    analysis_confidence: float = 0.0
    # review
    review_status: str = "pending"
    needs_review_reason: list[str] = field(default_factory=list)
    # meta
    analysis_pipeline: str = "rmvpe_direct"
    analysis_version: str = ANALYSIS_VERSION
    # süreler (analyze_audio doldurur)
    rmvpe_seconds: float | None = None
    postprocessing_seconds: float | None = None
    total_seconds: float | None = None
    # debug (production'a gitmez)
    segments: list[NoteSegment] = field(default_factory=list)


def analyze_frames(frames, audio_duration_seconds: float) -> AnalysisResult:
    """PitchFrames → AnalysisResult. RMVPE gerektirmez (sentetik frame ile test edilir)."""
    segments, stats = segment_notes(frames)
    range_result: RangeResult | None = compute_range(segments)

    segment_coverage = (
        sum(seg.duration for seg in segments) / audio_duration_seconds
        if audio_duration_seconds > 0
        else 0.0
    )

    reasons: list[str] = []
    if stats.valid_frames < MIN_VALID_FRAMES_FOR_RANGE:
        reasons.append("Çok az güvenilir melodik frame")
    if stats.octave_jump_ratio > MAX_OCTAVE_JUMP_RATIO:
        reasons.append("Pitch track çok parçalı (yüksek oktav-sıçrama oranı)")

    result = AnalysisResult(
        average_pitch_confidence=stats.average_pitch_confidence,
        voiced_frame_ratio=stats.voiced_frame_ratio,
        discarded_frame_ratio=stats.discarded_frame_ratio,
        octave_jump_ratio=stats.octave_jump_ratio,
        segments=segments,
    )

    if range_result is None:
        reasons.append("Güvenilir uç nota / tessitura belirlenemedi")
        result.analysis_confidence = compute_confidence(
            average_pitch_confidence=stats.average_pitch_confidence,
            voiced_frame_ratio=stats.voiced_frame_ratio,
            segment_coverage=segment_coverage,
            low_note_duration=0.0,
            high_note_duration=0.0,
            octave_jump_ratio=stats.octave_jump_ratio,
        )
    else:
        result.full_range_low_note = range_result.full_range_low_note
        result.full_range_high_note = range_result.full_range_high_note
        result.full_range_low_midi = range_result.full_range_low_midi
        result.full_range_high_midi = range_result.full_range_high_midi
        result.tessitura_low_note = range_result.tessitura_low_note
        result.tessitura_high_note = range_result.tessitura_high_note
        result.tessitura_low_midi = range_result.tessitura_low_midi
        result.tessitura_high_midi = range_result.tessitura_high_midi
        result.range_semitones = range_result.range_semitones
        result.low_note_timestamp = range_result.low_note_timestamp
        result.high_note_timestamp = range_result.high_note_timestamp
        result.low_note_duration = range_result.low_note_duration
        result.high_note_duration = range_result.high_note_duration
        result.analysis_confidence = compute_confidence(
            average_pitch_confidence=stats.average_pitch_confidence,
            voiced_frame_ratio=stats.voiced_frame_ratio,
            segment_coverage=segment_coverage,
            low_note_duration=range_result.low_note_duration,
            high_note_duration=range_result.high_note_duration,
            octave_jump_ratio=stats.octave_jump_ratio,
        )
        if range_result.range_semitones > SUSPICIOUS_RANGE_SEMITONES:
            reasons.append("Sıra dışı geniş aralık (şüpheli)")

    if result.analysis_confidence < NEEDS_REVIEW_CONFIDENCE:
        reasons.append("Düşük analiz güveni")

    result.needs_review_reason = reasons
    result.review_status = "needs_review" if reasons else "pending"
    return result


def analyze_audio(audio, sample_rate: int) -> AnalysisResult:
    """Gerçek ses → AnalysisResult. RMVPE'yi çalıştırır ve süreleri ölçer."""
    from .pitch import extract_f0

    import numpy as np

    audio = np.asarray(audio, dtype=np.float32)
    duration = len(audio) / sample_rate if sample_rate else 0.0

    t0 = time.perf_counter()
    frames = extract_f0(audio, sample_rate)
    t_rmvpe = time.perf_counter()
    result = analyze_frames(frames, duration)
    t_post = time.perf_counter()

    result.rmvpe_seconds = round(t_rmvpe - t0, 3)
    result.postprocessing_seconds = round(t_post - t_rmvpe, 3)
    result.total_seconds = round(t_post - t0, 3)
    return result


def build_debug_report(result: AnalysisResult) -> dict:
    """Tek dosya için ayrıntılı debug JSON'u (yalnızca lab, production'a gitmez)."""
    return {
        "summary": {
            "full_range": (
                f"{result.full_range_low_note}-{result.full_range_high_note}"
                if result.full_range_low_note
                else None
            ),
            "tessitura": (
                f"{result.tessitura_low_note}-{result.tessitura_high_note}"
                if result.tessitura_low_note
                else None
            ),
            "range_semitones": result.range_semitones,
            "analysis_confidence": result.analysis_confidence,
            "review_status": result.review_status,
            "needs_review_reason": result.needs_review_reason,
            "analysis_pipeline": result.analysis_pipeline,
            "analysis_version": result.analysis_version,
        },
        "extremes": {
            "low": {
                "note": result.full_range_low_note,
                "midi": result.full_range_low_midi,
                "timestamp": result.low_note_timestamp,
                "duration": result.low_note_duration,
            },
            "high": {
                "note": result.full_range_high_note,
                "midi": result.full_range_high_midi,
                "timestamp": result.high_note_timestamp,
                "duration": result.high_note_duration,
            },
        },
        "statistics": {
            "average_pitch_confidence": result.average_pitch_confidence,
            "voiced_frame_ratio": result.voiced_frame_ratio,
            "discarded_frame_ratio": result.discarded_frame_ratio,
            "segment_count": len(result.segments),
            "rmvpe_seconds": result.rmvpe_seconds,
            "postprocessing_seconds": result.postprocessing_seconds,
            "total_seconds": result.total_seconds,
        },
        "segments": [asdict(seg) for seg in result.segments],
    }
