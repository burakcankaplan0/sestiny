"""librosa.pyin tabanlı temel frekans (F0) çıkarımı ve üç test için analiz.

Bu modülün ürettiği sonuçlar tahminidir; CLAUDE.md gereği kesin veya tıbbi bir
teşhis olarak sunulmaz. Eşikler ve pencere uzunlukları klinik bir standarda
dayanmaz, deneyimsel başlangıç değerleridir (bkz. core/config.py yorumları).
"""

from dataclasses import dataclass

import librosa
import numpy as np

from app.core.config import (
    COMFORTABLE_RANGE_HIGH_PERCENTILE,
    COMFORTABLE_RANGE_LOW_PERCENTILE,
    GLIDE_COMFORTABLE_RANGE_MIN_CONFIDENCE,
    GLIDE_COMFORTABLE_RANGE_MIN_FRAMES,
    MAX_SEMITONE_JUMP,
    PYIN_FMAX_HZ,
    PYIN_FMIN_HZ,
    PYIN_FRAME_LENGTH,
    PYIN_HOP_LENGTH,
    STABILITY_CENTS_DIVISOR,
    STABILITY_DROPOUT_WEIGHT,
    STABILITY_JUMP_PENALTY,
    STABILITY_LABEL_MODERATE_MIN,
    STABILITY_LABEL_STABLE_MIN,
    STABILITY_LOW_VOICED_PENALTY,
    STABILITY_LOW_VOICED_RATIO_THRESHOLD,
    STABILITY_MAX_DEVIATION_PENALTY,
    STABILITY_MAX_DROPOUT_PENALTY,
    STABILITY_MAX_JUMP_PENALTY,
)
from app.services.music_theory import hz_array_to_midi, hz_to_note_name, midi_to_note_name


@dataclass(frozen=True)
class PitchTrack:
    """Bir kayıttan çıkarılan, temizlenmiş F0 dizisi ve yardımcı bilgiler.

    confidence: kaydın ne kadarında güvenilir bir şekilde perde takip edilebildiği
    (temiz frame sayısı / toplam frame sayısı). İstatistiksel bir güven aralığı
    değildir, yalnızca kapsama oranı temelli basit bir gösterge.
    """

    f0_hz: np.ndarray
    voiced_ratio: float
    jump_count: int
    dropout_ratio: float
    confidence: float


def extract_pitch_track(samples: np.ndarray, sample_rate: int) -> PitchTrack:
    """librosa.pyin ile F0 çıkarır; düşük güvenli ve fiziksel olarak anlamsız
    (aşırı sıçrayan) frame'leri eler."""
    if len(samples) < PYIN_FRAME_LENGTH:
        return PitchTrack(f0_hz=np.array([]), voiced_ratio=0.0, jump_count=0, dropout_ratio=1.0, confidence=0.0)

    f0, voiced_flag, voiced_prob = librosa.pyin(
        samples,
        fmin=PYIN_FMIN_HZ,
        fmax=PYIN_FMAX_HZ,
        sr=sample_rate,
        frame_length=PYIN_FRAME_LENGTH,
        hop_length=PYIN_HOP_LENGTH,
    )

    total_frames = len(f0)
    if total_frames == 0:
        return PitchTrack(f0_hz=np.array([]), voiced_ratio=0.0, jump_count=0, dropout_ratio=1.0, confidence=0.0)

    times = librosa.frames_to_time(np.arange(total_frames), sr=sample_rate, hop_length=PYIN_HOP_LENGTH)
    hop_seconds = PYIN_HOP_LENGTH / sample_rate

    voiced_ratio = float(np.mean(voiced_flag))

    reliable = voiced_flag & (voiced_prob >= 0.5) & ~np.isnan(f0)
    reliable_f0 = f0[reliable]
    reliable_times = times[reliable]

    cleaned_f0, jump_count = _remove_pitch_jumps(reliable_f0, reliable_times, hop_seconds)

    dropout_ratio = 1.0 - (len(cleaned_f0) / total_frames)
    confidence = round(max(0.0, min(1.0, len(cleaned_f0) / total_frames)), 2)

    return PitchTrack(
        f0_hz=cleaned_f0,
        voiced_ratio=round(voiced_ratio, 2),
        jump_count=jump_count,
        dropout_ratio=round(dropout_ratio, 2),
        confidence=confidence,
    )


def _remove_pitch_jumps(
    f0: np.ndarray, times: np.ndarray, hop_seconds: float
) -> tuple[np.ndarray, int]:
    """Zamanda birbirine yakın (aynı sesli bölüm içindeki) ardışık frame'ler arasında
    MAX_SEMITONE_JUMP'tan büyük sıçramaları eler (muhtemel oktav hatası).

    Aralarında sessiz bir boşluk olan frame'ler (örn. konuşmadaki iki ayrı hece)
    birbirine göre sıçrama olarak değerlendirilmez — bu, gerçek ve makul perde
    değişimlerinin yanlışlıkla silinmesini önler.
    """
    if len(f0) == 0:
        return f0, 0

    max_gap_seconds = hop_seconds * 1.5
    kept_f0 = [f0[0]]
    kept_times = [times[0]]
    jump_count = 0

    for i in range(1, len(f0)):
        previous_f0 = kept_f0[-1]
        previous_time = kept_times[-1]
        current_f0 = f0[i]
        current_time = times[i]

        same_segment = (current_time - previous_time) <= max_gap_seconds
        if same_segment:
            semitone_diff = abs(12 * np.log2(current_f0 / previous_f0))
            if semitone_diff > MAX_SEMITONE_JUMP:
                jump_count += 1
                continue

        kept_f0.append(current_f0)
        kept_times.append(current_time)

    return np.array(kept_f0), jump_count


def _median_absolute_deviation_semitones(f0_hz: np.ndarray) -> float:
    midi_values = hz_array_to_midi(f0_hz)
    return float(np.median(np.abs(midi_values - np.median(midi_values))))


# ---------- Test 1: Konuşma ----------


@dataclass(frozen=True)
class SpeechAnalysis:
    median_f0_hz: float | None
    approximate_note: str | None
    pitch_variability_semitones: float | None
    voiced_ratio: float
    confidence: float


def analyze_speech(samples: np.ndarray, sample_rate: int) -> SpeechAnalysis:
    track = extract_pitch_track(samples, sample_rate)

    if len(track.f0_hz) == 0:
        return SpeechAnalysis(
            median_f0_hz=None,
            approximate_note=None,
            pitch_variability_semitones=None,
            voiced_ratio=track.voiced_ratio,
            confidence=track.confidence,
        )

    median_hz = float(np.median(track.f0_hz))
    variability = _median_absolute_deviation_semitones(track.f0_hz)

    return SpeechAnalysis(
        median_f0_hz=round(median_hz, 1),
        approximate_note=hz_to_note_name(median_hz),
        pitch_variability_semitones=round(variability, 2),
        voiced_ratio=track.voiced_ratio,
        confidence=track.confidence,
    )


# ---------- Test 2: Uzun "A" sesi ----------


def compute_stability_score(
    *, deviation_cents: float, dropout_ratio: float, jump_count: int, voiced_ratio: float
) -> int:
    """0-100 arası basit bir stabilite skoru.

    Klinik/bilimsel bir standart değildir; yalnızca "sesi ne kadar sabit
    tutabildin" hissini kabaca vermek için tasarlanmış bir sezgiseldir
    (bkz. CLAUDE.md bölüm 13).
    """
    score = 100.0
    score -= min(STABILITY_MAX_DEVIATION_PENALTY, deviation_cents / STABILITY_CENTS_DIVISOR)
    score -= min(STABILITY_MAX_DROPOUT_PENALTY, dropout_ratio * STABILITY_DROPOUT_WEIGHT)
    score -= min(STABILITY_MAX_JUMP_PENALTY, jump_count * STABILITY_JUMP_PENALTY)
    if voiced_ratio < STABILITY_LOW_VOICED_RATIO_THRESHOLD:
        score -= STABILITY_LOW_VOICED_PENALTY
    return int(max(0, min(100, round(score))))


def stability_label_for_score(score: int) -> str:
    if score >= STABILITY_LABEL_STABLE_MIN:
        return "stabil"
    if score >= STABILITY_LABEL_MODERATE_MIN:
        return "orta düzeyde stabil"
    return "geliştirilebilir"


@dataclass(frozen=True)
class SustainedVowelAnalysis:
    median_f0_hz: float | None
    approximate_note: str | None
    voiced_duration_seconds: float
    pitch_deviation_cents: float | None
    jump_count: int
    dropout_ratio: float
    stability_score: int
    stability_label: str
    confidence: float


def analyze_sustained_vowel(samples: np.ndarray, sample_rate: int) -> SustainedVowelAnalysis:
    track = extract_pitch_track(samples, sample_rate)
    total_duration = len(samples) / sample_rate if sample_rate > 0 else 0.0
    voiced_duration = round(track.voiced_ratio * total_duration, 2)

    if len(track.f0_hz) == 0:
        score = compute_stability_score(
            deviation_cents=0.0, dropout_ratio=1.0, jump_count=track.jump_count, voiced_ratio=track.voiced_ratio
        )
        return SustainedVowelAnalysis(
            median_f0_hz=None,
            approximate_note=None,
            voiced_duration_seconds=voiced_duration,
            pitch_deviation_cents=None,
            jump_count=track.jump_count,
            dropout_ratio=track.dropout_ratio,
            stability_score=score,
            stability_label=stability_label_for_score(score),
            confidence=track.confidence,
        )

    median_hz = float(np.median(track.f0_hz))
    deviation_cents = _median_absolute_deviation_semitones(track.f0_hz) * 100

    score = compute_stability_score(
        deviation_cents=deviation_cents,
        dropout_ratio=track.dropout_ratio,
        jump_count=track.jump_count,
        voiced_ratio=track.voiced_ratio,
    )

    return SustainedVowelAnalysis(
        median_f0_hz=round(median_hz, 1),
        approximate_note=hz_to_note_name(median_hz),
        voiced_duration_seconds=voiced_duration,
        pitch_deviation_cents=round(deviation_cents, 1),
        jump_count=track.jump_count,
        dropout_ratio=track.dropout_ratio,
        stability_score=score,
        stability_label=stability_label_for_score(score),
        confidence=track.confidence,
    )


# ---------- Test 3: Kalından inceye kaydırma (glide) ----------


@dataclass(frozen=True)
class GlideAnalysis:
    observed_low_note: str | None
    observed_high_note: str | None
    observed_low_midi: int | None
    observed_high_midi: int | None
    range_semitones: int | None
    estimated_comfortable_low_note: str | None
    estimated_comfortable_high_note: str | None
    confidence: float


def analyze_glide(samples: np.ndarray, sample_rate: int) -> GlideAnalysis:
    track = extract_pitch_track(samples, sample_rate)

    if len(track.f0_hz) == 0:
        return GlideAnalysis(
            observed_low_note=None,
            observed_high_note=None,
            observed_low_midi=None,
            observed_high_midi=None,
            range_semitones=None,
            estimated_comfortable_low_note=None,
            estimated_comfortable_high_note=None,
            confidence=track.confidence,
        )

    midi_values = hz_array_to_midi(track.f0_hz)
    low_midi = int(round(float(np.min(midi_values))))
    high_midi = int(round(float(np.max(midi_values))))

    comfortable_low_note = None
    comfortable_high_note = None
    has_enough_data = len(midi_values) >= GLIDE_COMFORTABLE_RANGE_MIN_FRAMES
    has_enough_confidence = track.confidence >= GLIDE_COMFORTABLE_RANGE_MIN_CONFIDENCE
    if has_enough_data and has_enough_confidence:
        low_percentile = float(np.percentile(midi_values, COMFORTABLE_RANGE_LOW_PERCENTILE))
        high_percentile = float(np.percentile(midi_values, COMFORTABLE_RANGE_HIGH_PERCENTILE))
        comfortable_low_note = midi_to_note_name(low_percentile)
        comfortable_high_note = midi_to_note_name(high_percentile)

    return GlideAnalysis(
        observed_low_note=midi_to_note_name(low_midi),
        observed_high_note=midi_to_note_name(high_midi),
        observed_low_midi=low_midi,
        observed_high_midi=high_midi,
        range_semitones=high_midi - low_midi,
        estimated_comfortable_low_note=comfortable_low_note,
        estimated_comfortable_high_note=comfortable_high_note,
        confidence=track.confidence,
    )
