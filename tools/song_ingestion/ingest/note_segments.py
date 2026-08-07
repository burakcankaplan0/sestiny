"""Frame-level F0 → güvenilir nota segmentleri.

Ham min/max F0 ASLA doğrudan kullanılmaz (bkz. plan). Adımlar:
1. Güvensiz / aralık-dışı frame'ler atılır.
2. MIDI dizisine hafif medyan yumuşatma + en yakın yarım tona yuvarlama.
3. Ardışık, aynı-notalı (ve zamanda yakın) frame'ler bir segmentte birleşir.
4. Yeterli süre/frame taşımayan segmentler (spike'lar) elenir.

Yuvarlayarak segmentleme, glide'ı doğal biçimde ele alır: glide her yarım
tondan kısa süre geçer → her yarım ton kısa bir segment olur; min-süre eşiği
geçiş notalarını eler, glide binlerce parçaya bölünmez.

Yalnızca numpy kullanır (RMVPE gerektirmez) — sentetik frame'lerle test edilebilir.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..config import (
    MAX_SEGMENT_GAP_SECONDS,
    MEDIAN_SMOOTH_FRAMES,
    MIN_NOTE_DURATION_SECONDS,
    MIN_PITCH_CONFIDENCE,
    MIN_SUPPORTING_FRAMES,
    MIN_VALID_F0_HZ,
    MAX_VALID_F0_HZ,
)
from ..notes import midi_to_note_name

A4_HZ = 440.0
A4_MIDI = 69


@dataclass(frozen=True)
class NoteSegment:
    midi: int
    note_name: str
    start_time: float
    end_time: float
    duration: float
    frame_count: int
    median_f0: float
    median_confidence: float
    pitch_deviation_cents: float


@dataclass(frozen=True)
class FilterStats:
    total_frames: int
    valid_frames: int
    voiced_frame_ratio: float
    discarded_frame_ratio: float
    average_pitch_confidence: float  # kabul edilen frame'lerin ortalaması
    octave_jump_ratio: float  # ardışık geçerli frame'ler arası büyük sıçrama oranı


def _median_filter(values: np.ndarray, window: int) -> np.ndarray:
    """Basit kayan medyan (kenarlarda pencere kısalır). scipy gerektirmez."""
    if window <= 1 or len(values) == 0:
        return values
    half = window // 2
    out = np.empty_like(values)
    for i in range(len(values)):
        lo = max(0, i - half)
        hi = min(len(values), i + half + 1)
        out[i] = np.median(values[lo:hi])
    return out


def _filter_frames(frames) -> tuple[np.ndarray, np.ndarray, np.ndarray, FilterStats]:
    """Geçerli (times, midi, confidence) döndürür + filtreleme istatistikleri.

    `frames` PitchFrames benzeri: .times, .f0_hz, .confidence numpy dizileri.
    """
    from ..config import MAX_FRAME_JUMP_SEMITONES

    times = np.asarray(frames.times, dtype=np.float64)
    f0 = np.asarray(frames.f0_hz, dtype=np.float64)
    conf = np.asarray(frames.confidence, dtype=np.float64)
    total = len(f0)

    with np.errstate(invalid="ignore"):
        valid_mask = (
            (conf >= MIN_PITCH_CONFIDENCE)
            & (f0 >= MIN_VALID_F0_HZ)
            & (f0 <= MAX_VALID_F0_HZ)
            & np.isfinite(f0)
        )

    v_times = times[valid_mask]
    v_f0 = f0[valid_mask]
    v_conf = conf[valid_mask]
    v_midi = A4_MIDI + 12 * np.log2(v_f0 / A4_HZ) if len(v_f0) else np.array([])

    valid_frames = len(v_f0)
    voiced_ratio = valid_frames / total if total else 0.0
    discarded_ratio = 1.0 - voiced_ratio
    avg_conf = float(np.mean(v_conf)) if valid_frames else 0.0

    # Oktav-sıçrama oranı: ardışık geçerli frame'ler (zamanda yakın) arasında
    # MAX_FRAME_JUMP_SEMITONES üstü fark oranı — parçalı/hatalı pitch göstergesi.
    jumps = 0
    comparisons = 0
    for i in range(1, valid_frames):
        if v_times[i] - v_times[i - 1] <= MAX_SEGMENT_GAP_SECONDS:
            comparisons += 1
            if abs(v_midi[i] - v_midi[i - 1]) > MAX_FRAME_JUMP_SEMITONES:
                jumps += 1
    jump_ratio = jumps / comparisons if comparisons else 0.0

    stats = FilterStats(
        total_frames=total,
        valid_frames=valid_frames,
        voiced_frame_ratio=round(voiced_ratio, 4),
        discarded_frame_ratio=round(discarded_ratio, 4),
        average_pitch_confidence=round(avg_conf, 4),
        octave_jump_ratio=round(jump_ratio, 4),
    )
    return v_times, v_midi, v_conf, stats


def segment_notes(frames) -> tuple[list[NoteSegment], FilterStats]:
    """Frame'leri güvenilir nota segmentlerine dönüştürür + filtre istatistikleri."""
    v_times, v_midi, v_conf, stats = _filter_frames(frames)
    if len(v_midi) == 0:
        return [], stats

    hop = float(np.median(np.diff(v_times))) if len(v_times) > 1 else 0.01
    smoothed = _median_filter(v_midi, MEDIAN_SMOOTH_FRAMES)
    rounded = np.rint(smoothed).astype(int)

    raw_segments: list[dict] = []
    current: dict | None = None
    for i in range(len(rounded)):
        midi_i = int(rounded[i])
        t_i = float(v_times[i])
        if (
            current is not None
            and midi_i == current["midi"]
            and (t_i - current["last_time"]) <= MAX_SEGMENT_GAP_SECONDS
        ):
            current["last_time"] = t_i
            current["idx"].append(i)
        else:
            if current is not None:
                raw_segments.append(current)
            current = {"midi": midi_i, "start": t_i, "last_time": t_i, "idx": [i]}
    if current is not None:
        raw_segments.append(current)

    segments: list[NoteSegment] = []
    for seg in raw_segments:
        idx = seg["idx"]
        frame_count = len(idx)
        duration = (seg["last_time"] - seg["start"]) + hop  # son frame'in de süresi
        if duration < MIN_NOTE_DURATION_SECONDS or frame_count < MIN_SUPPORTING_FRAMES:
            continue
        seg_midi_frac = v_midi[idx]
        seg_conf = v_conf[idx]
        median_midi = float(np.median(seg_midi_frac))
        deviation_cents = float(np.median(np.abs(seg_midi_frac - median_midi)) * 100)
        median_f0 = float(A4_HZ * 2 ** ((median_midi - A4_MIDI) / 12))
        segments.append(
            NoteSegment(
                midi=int(seg["midi"]),
                note_name=midi_to_note_name(seg["midi"]),
                start_time=round(seg["start"], 3),
                end_time=round(seg["last_time"] + hop, 3),
                duration=round(duration, 3),
                frame_count=frame_count,
                median_f0=round(median_f0, 2),
                median_confidence=round(float(np.median(seg_conf)), 3),
                pitch_deviation_cents=round(deviation_cents, 1),
            )
        )
    return segments, stats
