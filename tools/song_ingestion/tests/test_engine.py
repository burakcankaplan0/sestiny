"""Direct RMVPE analiz motoru — sentetik frame testleri (RMVPE gerektirmez).

Motor mantığı (filtreleme → segmentasyon → range → tessitura → confidence →
needs_review) kontrollü, deterministik pitch frame dizileriyle test edilir.
Gerçek RMVPE ayrı bir entegrasyon testinde (test_rmvpe_integration.py) denenir.

Bu testler yalnızca numpy gerektirir; backend/.venv (numpy + pytest içerir) ile
koşulabilir — böylece tüm lab test paketi tek komutla çalışır.
"""

from dataclasses import dataclass

import numpy as np

from tools.song_ingestion.config import RMVPE_SAMPLE_RATE  # noqa: F401 (paket importu doğrulaması)
from tools.song_ingestion.ingest.engine import analyze_frames, build_debug_report

HOP = 0.01
A4_HZ = 440.0
A4_MIDI = 69


def _midi_to_hz(midi: float) -> float:
    return A4_HZ * 2 ** ((midi - A4_MIDI) / 12)


@dataclass
class FakeFrames:
    times: np.ndarray
    f0_hz: np.ndarray
    confidence: np.ndarray
    model: str = "synthetic"


class _Builder:
    """10 ms frame dizileri kurar. Nota/spike/glide/sessizlik ekleyebilir."""

    def __init__(self):
        self.f0: list[float] = []
        self.conf: list[float] = []

    def note(self, midi: float, dur: float, conf: float = 0.9):
        n = int(round(dur / HOP))
        self.f0 += [_midi_to_hz(midi)] * n
        self.conf += [conf] * n
        return self

    def glide(self, midi_from: float, midi_to: float, dur: float, conf: float = 0.9):
        n = int(round(dur / HOP))
        for i in range(n):
            midi = midi_from + (midi_to - midi_from) * i / max(1, n - 1)
            self.f0.append(_midi_to_hz(midi))
            self.conf.append(conf)
        return self

    def silence(self, dur: float, conf: float = 0.05):
        n = int(round(dur / HOP))
        self.f0 += [0.0] * n
        self.conf += [conf] * n
        return self

    def build(self) -> FakeFrames:
        f0 = np.array(self.f0, dtype=np.float64)
        conf = np.array(self.conf, dtype=np.float64)
        times = np.arange(len(f0), dtype=np.float64) * HOP
        return FakeFrames(times=times, f0_hz=f0, confidence=conf)

    @property
    def duration(self) -> float:
        return len(self.f0) * HOP


def _analyze(builder: _Builder):
    frames = builder.build()
    return analyze_frames(frames, builder.duration)


# A) Sabit A3 → yaklaşık A3 segmenti, full range A3-A3
def test_constant_a3():
    b = _Builder().note(57, 1.0)  # A3
    r = _analyze(b)
    assert r.full_range_low_note == "A3"
    assert r.full_range_high_note == "A3"
    assert r.review_status == "pending"
    assert r.analysis_confidence > 0.6


# B) A3 → C4 → E4 → üç nota segmenti, full range A3-E4
def test_three_notes_a3_c4_e4():
    b = _Builder().note(57, 0.5).note(60, 0.5).note(64, 0.5)
    r = _analyze(b)
    assert len(r.segments) == 3
    assert [s.note_name for s in r.segments] == ["A3", "C4", "E4"]
    assert r.full_range_low_note == "A3"
    assert r.full_range_high_note == "E4"
    assert r.range_semitones == 7


# C) A3 içinde 20 ms F6 spike → F6 full range'e girmemeli
def test_short_spike_is_rejected():
    b = _Builder().note(57, 0.5).note(89, 0.02).note(57, 0.5)  # F6 (89) sadece 20 ms
    r = _analyze(b)
    assert r.full_range_high_note == "A3"
    assert all(s.note_name != "F6" for s in r.segments)


# D) Uzun C4 + kısa yüksek G5 → G5 uç-nota eşiğinin altındaysa high note olmamalı
def test_short_high_note_is_not_full_range_top():
    # G5 (79) 90 ms: geçerli segment ama EXTREME_MIN_DURATION (140 ms) altında.
    b = _Builder().note(60, 1.0).note(79, 0.09)
    r = _analyze(b)
    assert r.full_range_high_note == "C4"  # G5 değil
    # G5 yine de geçerli bir segment olarak görünür (tessitura'ya girer ama uç değil)
    assert any(s.note_name == "G5" for s in r.segments)


# E) A3–A4 glide → binlerce segmente parçalanmamalı; range ~A3-A4
def test_glide_is_not_shattered():
    b = _Builder().glide(57, 69, 2.0)  # A3 → A4
    r = _analyze(b)
    # Glide 13 yarı tondan geçer → ~13 segment, binlerce DEĞİL.
    assert len(r.segments) <= 20
    # Saf glide'da en uç notalara yalnızca yarım yarım-ton süresi kadar (~77 ms)
    # dokunulur; bu uç-nota eşiğinin (140 ms) altında kaldığı için uçtan bir
    # yarım ton kırpılabilir — bu, "anlık dokunulan ucu şişirme" ilkesinin
    # (kullanıcı 2. madde) beklenen sonucu. Aralık yine de ~A3-A4 olmalı.
    assert r.full_range_low_midi in (57, 58)   # A3 veya A#3
    assert r.full_range_high_midi in (68, 69)  # G#4 veya A4
    assert r.range_semitones >= 10


# F) Sessiz / düşük güven → güvenilir range uydurulmamalı
def test_silence_produces_no_range():
    b = _Builder().silence(1.0)
    r = _analyze(b)
    assert r.full_range_low_note is None
    assert r.review_status == "needs_review"
    assert any("belirlenemedi" in reason for reason in r.needs_review_reason)


def test_low_confidence_produces_no_range():
    # Frame'ler var ama hepsi güven eşiğinin altında → geçerli frame yok.
    b = _Builder().note(60, 1.0, conf=0.2)
    r = _analyze(b)
    assert r.full_range_low_note is None
    assert r.review_status == "needs_review"


def test_tessitura_excludes_one_off_adlib():
    # Uzun A3 bloğu + tek bir yüksek E5 ad-lib (uç-eşiği geçecek kadar uzun ama
    # süre-ağırlıklı merkez A3 çevresinde kalmalı).
    b = _Builder().note(57, 3.0).note(76, 0.2)  # E5 ad-lib
    r = _analyze(b)
    # Full range A3-E5 olabilir ama tessitura yalnızca A3 çevresinde kalmalı.
    assert r.tessitura_high_note == "A3"
    assert r.full_range_high_note == "E5"


def test_debug_report_shape():
    b = _Builder().note(57, 0.5).note(60, 0.5)
    r = _analyze(b)
    report = build_debug_report(r)
    assert set(report.keys()) == {"summary", "extremes", "statistics", "segments"}
    assert report["extremes"]["low"]["note"] == "A3"
    assert isinstance(report["segments"], list) and len(report["segments"]) == 2
