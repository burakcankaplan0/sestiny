"""librosa.pyin tabanlı analiz fonksiyonlarının sentetik seslerle testleri.

CLAUDE.md madde 15'te istenen otomatik sentetik ses testleri: A3/C4 nota tespiti,
stabil/dalgalanan sinüs stabilitesi, glide benzeri ses üzerinde alt/üst nota.
Gerçek ses dosyası kullanılmaz; tüm sesler numpy ile kodda üretilir.
"""

import numpy as np
import pytest

from app.core.config import TARGET_SAMPLE_RATE
from app.services.pitch_analysis import analyze_glide, analyze_speech, analyze_sustained_vowel

SR = TARGET_SAMPLE_RATE


def _sine(freq: float, duration_s: float, amplitude: float = 0.4) -> np.ndarray:
    n = int(SR * duration_s)
    t = np.arange(n) / SR
    return (amplitude * np.sin(2 * np.pi * freq * t)).astype(np.float32)


def _wavering_sine(
    base_freq: float, duration_s: float, wobble_hz: float = 6.0, wobble_rate_hz: float = 3.0, amplitude: float = 0.4
) -> np.ndarray:
    """Frekansı periyodik olarak sallanan (vibrato benzeri) sentetik ses."""
    n = int(SR * duration_s)
    t = np.arange(n) / SR
    instantaneous_freq = base_freq + wobble_hz * np.sin(2 * np.pi * wobble_rate_hz * t)
    phase = 2 * np.pi * np.cumsum(instantaneous_freq) / SR
    return (amplitude * np.sin(phase)).astype(np.float32)


def _chirp(freq_low: float, freq_high: float, duration_s: float, amplitude: float = 0.4) -> np.ndarray:
    """Kalından inceye doğru düz bir frekans kayması — glide testinin sentetik karşılığı."""
    n = int(SR * duration_s)
    t = np.arange(n) / SR
    instantaneous_freq = freq_low + (freq_high - freq_low) * (t / duration_s)
    phase = 2 * np.pi * np.cumsum(instantaneous_freq) / SR
    return (amplitude * np.sin(phase)).astype(np.float32)


def test_a3_sine_wave_is_detected_correctly():
    result = analyze_speech(_sine(220.0, 4.0), SR)

    assert result.approximate_note == "A3"
    assert result.median_f0_hz == pytest.approx(220.0, rel=0.02)
    assert result.confidence > 0.5


def test_c4_sine_wave_is_detected_correctly():
    result = analyze_speech(_sine(261.63, 4.0), SR)

    assert result.approximate_note == "C4"
    assert result.median_f0_hz == pytest.approx(261.63, rel=0.02)


def test_stable_sine_gets_high_stability_score():
    result = analyze_sustained_vowel(_sine(180.0, 6.0), SR)

    assert result.stability_score >= 80
    assert result.stability_label == "stabil"


def test_wavering_sine_gets_lower_stability_score_than_stable():
    stable = analyze_sustained_vowel(_sine(180.0, 6.0), SR)
    wavering = analyze_sustained_vowel(_wavering_sine(180.0, 6.0), SR)

    assert wavering.stability_score < stable.stability_score


def test_silent_signal_produces_no_fabricated_note():
    samples = np.zeros(int(SR * 3.0), dtype=np.float32)
    result = analyze_speech(samples, SR)

    assert result.median_f0_hz is None
    assert result.approximate_note is None
    assert result.confidence == 0.0


def test_glide_detects_approximate_low_and_high_notes():
    # G2 (~98 Hz) - E4 (~330 Hz) arası düz bir kayma; CLAUDE.md'nin kendi örnek
    # aralığıyla (G2-E4, 21 yarı ton) aynı.
    result = analyze_glide(_chirp(98.0, 330.0, 8.0), SR)

    assert result.observed_low_midi is not None
    assert result.observed_high_midi is not None
    # G2 = MIDI 43, E4 = MIDI 64. Chirp'in uçlarında pyin'in penceresi biraz
    # yumuşatma yapabilir; birkaç yarı ton tolerans bırakılıyor.
    assert abs(result.observed_low_midi - 43) <= 3
    assert abs(result.observed_high_midi - 64) <= 3
    assert result.observed_low_note is not None
    assert result.observed_high_note is not None


def test_glide_with_sufficient_data_estimates_comfortable_range():
    result = analyze_glide(_chirp(98.0, 330.0, 8.0), SR)

    assert result.estimated_comfortable_low_note is not None
    assert result.estimated_comfortable_high_note is not None


def test_glide_on_silence_does_not_fabricate_range():
    samples = np.zeros(int(SR * 5.0), dtype=np.float32)
    result = analyze_glide(samples, SR)

    assert result.observed_low_note is None
    assert result.observed_high_note is None
    assert result.estimated_comfortable_low_note is None
    assert result.estimated_comfortable_high_note is None
