"""RMVPE'yi GERÇEKTEN çalıştıran entegrasyon testi.

`rmvpe_onnx` yalnızca lab venv'inde kuruludur; backend/.venv ile koşulan ana
test paketinde bu test `importorskip` ile atlanır. Lab venv'iyle çalıştırıldığında
sentetik bir sabit tonu uçtan uca (ses → RMVPE → analiz motoru) işler ve doğru
notayı bulduğunu doğrular.

Çalıştırma (lab venv):
    tools/song_ingestion/venv/bin/python -m pytest tools/song_ingestion/tests/test_rmvpe_integration.py
"""

import numpy as np
import pytest

pytest.importorskip("rmvpe_onnx", reason="rmvpe-onnx yalnızca lab venv'inde kurulu")

from tools.song_ingestion.config import RMVPE_SAMPLE_RATE
from tools.song_ingestion.ingest.engine import analyze_audio


def _sine(midi: float, seconds: float, sr: int) -> np.ndarray:
    freq = 440.0 * 2 ** ((midi - 69) / 12)
    t = np.arange(int(seconds * sr)) / sr
    return (0.5 * np.sin(2 * np.pi * freq * t)).astype(np.float32)


def test_rmvpe_detects_constant_tone_end_to_end():
    # A3 (220 Hz) sabit ton, 2 saniye.
    audio = _sine(57, 2.0, RMVPE_SAMPLE_RATE)
    result = analyze_audio(audio, RMVPE_SAMPLE_RATE)

    assert result.full_range_low_midi is not None, "RMVPE bir aralık bulmalı"
    # ±1 yarı ton tolerans: sentetik ton A3=57 civarında olmalı.
    assert abs(result.full_range_low_midi - 57) <= 1
    assert abs(result.full_range_high_midi - 57) <= 1
    assert result.rmvpe_seconds is not None and result.rmvpe_seconds > 0
