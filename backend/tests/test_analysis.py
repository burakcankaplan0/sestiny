"""POST /api/v1/analyze-session testleri.

Gerçek ses dosyası kullanılmaz; tüm sesler testler sırasında sentetik olarak
(sinüs dalgası, sessizlik, tam ölçekli kare dalga) üretilir. Bu, CLAUDE.md'nin
"test deposuna gereksiz büyük ses dosyaları koyma" kuralına uyar.
"""

import glob
import io
import math
import os
import struct
import tempfile
import wave

from fastapi.testclient import TestClient

from app.core.config import API_V1_PREFIX, get_settings
from app.main import app

client = TestClient(app)

SAMPLE_RATE = 44100


def _sine_wav_bytes(freq: float, duration_s: float, amplitude: float = 0.5) -> bytes:
    n = int(SAMPLE_RATE * duration_s)
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        frames = bytearray()
        for i in range(n):
            value = int(amplitude * 32767 * math.sin(2 * math.pi * freq * i / SAMPLE_RATE))
            frames += struct.pack("<h", value)
        wf.writeframes(bytes(frames))
    return buffer.getvalue()


def _silence_wav_bytes(duration_s: float) -> bytes:
    n = int(SAMPLE_RATE * duration_s)
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(b"\x00\x00" * n)
    return buffer.getvalue()


def _clipped_wav_bytes(duration_s: float) -> bytes:
    """Tüm örnekler tam ölçekte — clipping oranı reddi tetiklemesi beklenen sentetik ses."""
    n = int(SAMPLE_RATE * duration_s)
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        frames = bytearray()
        for i in range(n):
            value = 32767 if (i // 4) % 2 == 0 else -32768
            frames += struct.pack("<h", value)
        wf.writeframes(bytes(frames))
    return buffer.getvalue()


def _valid_session_files() -> dict:
    """Üç testin de minimum süresini rahatça karşılayan, temiz sinüs kayıtları."""
    return {
        "speech": ("speech.wav", io.BytesIO(_sine_wav_bytes(150, 4.0)), "audio/wav"),
        "sustained_vowel": ("vowel.wav", io.BytesIO(_sine_wav_bytes(180, 3.0)), "audio/wav"),
        "glide": ("glide.wav", io.BytesIO(_sine_wav_bytes(200, 4.0)), "audio/wav"),
    }


def test_valid_recordings_are_accepted():
    response = client.post(f"{API_V1_PREFIX}/analyze-session", files=_valid_session_files())
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "accepted"
    for test_id in ("speech", "sustained_vowel", "glide"):
        assert body[test_id]["accepted"] is True
        assert body[test_id]["duration_seconds"] > 0


def test_unsupported_format_is_rejected():
    files = _valid_session_files()
    files["speech"] = ("speech.txt", io.BytesIO(b"bu bir ses dosyasi degil"), "text/plain")

    response = client.post(f"{API_V1_PREFIX}/analyze-session", files=files)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "rejected"
    assert body["speech"]["accepted"] is False
    assert "desteklenmiyor" in body["speech"]["warnings"][0]


def test_too_short_recording_is_rejected():
    files = _valid_session_files()
    files["speech"] = ("speech.wav", io.BytesIO(_sine_wav_bytes(150, 0.5)), "audio/wav")

    response = client.post(f"{API_V1_PREFIX}/analyze-session", files=files)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "rejected"
    assert body["speech"]["accepted"] is False
    assert any("kısa" in warning for warning in body["speech"]["warnings"])


def test_silent_recording_is_rejected():
    files = _valid_session_files()
    files["sustained_vowel"] = ("vowel.wav", io.BytesIO(_silence_wav_bytes(3.0)), "audio/wav")

    response = client.post(f"{API_V1_PREFIX}/analyze-session", files=files)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "rejected"
    assert body["sustained_vowel"]["accepted"] is False
    assert any("düşük" in warning for warning in body["sustained_vowel"]["warnings"])


def test_clipped_recording_is_rejected():
    files = _valid_session_files()
    files["glide"] = ("glide.wav", io.BytesIO(_clipped_wav_bytes(4.0)), "audio/wav")

    response = client.post(f"{API_V1_PREFIX}/analyze-session", files=files)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "rejected"
    assert body["glide"]["accepted"] is False
    assert any("bozulmuş" in warning for warning in body["glide"]["warnings"])


def test_oversized_file_is_rejected_with_413():
    max_bytes = get_settings().max_upload_bytes
    oversized = io.BytesIO(b"0" * (max_bytes + 1024))

    files = _valid_session_files()
    files["speech"] = ("speech.wav", oversized, "audio/wav")

    response = client.post(f"{API_V1_PREFIX}/analyze-session", files=files)

    assert response.status_code == 413


def test_temp_files_are_cleaned_up():
    pattern = os.path.join(tempfile.gettempdir(), "sestiny_*")
    before = set(glob.glob(pattern))

    response = client.post(f"{API_V1_PREFIX}/analyze-session", files=_valid_session_files())
    assert response.status_code == 200

    after = set(glob.glob(pattern))
    assert after == before, "Analiz sonrası geçici dosya kalmamalı"


def test_response_schema_has_expected_fields():
    response = client.post(f"{API_V1_PREFIX}/analyze-session", files=_valid_session_files())
    body = response.json()

    assert set(body.keys()) == {"session_id", "status", "speech", "sustained_vowel", "glide"}
    for test_id in ("speech", "sustained_vowel", "glide"):
        assert set(body[test_id].keys()) == {
            "accepted",
            "overall_score",
            "label",
            "warnings",
            "duration_seconds",
        }
