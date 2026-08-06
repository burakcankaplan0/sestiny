"""POST /api/v1/analyze-session hız sınırlama testleri.

Not: Zaman penceresinin gerçekten dolup sıfırlandığı (ör. bir dakika sonra
tekrar istek göndermenin başarılı olduğu) burada test EDİLMEDİ — bunun için
zamanı taklit eden bir kütüphane (freezegun) gerekir, bu projede yok. Bu
açıkça doğrulanamayan bir nokta olarak docs/PROGRESS.md'de belirtiliyor
(bkz. K-046'daki dürüstlük ilkesiyle aynı yaklaşım).
"""

import io

from fastapi.testclient import TestClient

from app.core.config import ANALYZE_SESSION_RATE_LIMIT, API_V1_PREFIX
from app.core.rate_limit import RATE_LIMIT_MESSAGE
from app.main import app

client = TestClient(app)

# "5/minute" -> 5. Sayı config'ten türetilir ki eşik değişirse test de uyum sağlasın.
_RATE_LIMIT_COUNT = int(ANALYZE_SESSION_RATE_LIMIT.split("/")[0])


def _garbage_files() -> dict:
    """Desteklenmeyen format — kalite kontrolünde hızla reddedilir (200 döner),
    ama yine de hız sınırlayıcıya karşı sayılır; testi hızlı tutar."""
    garbage = ("bad.txt", io.BytesIO(b"ses degil"), "text/plain")
    return {"speech": garbage, "sustained_vowel": garbage, "glide": garbage}


def test_requests_within_limit_are_not_blocked():
    for _ in range(_RATE_LIMIT_COUNT):
        response = client.post(f"{API_V1_PREFIX}/analyze-session", files=_garbage_files())
        assert response.status_code != 429


def test_request_past_limit_is_rejected_with_429_and_turkish_message():
    for _ in range(_RATE_LIMIT_COUNT):
        client.post(f"{API_V1_PREFIX}/analyze-session", files=_garbage_files())

    response = client.post(f"{API_V1_PREFIX}/analyze-session", files=_garbage_files())

    assert response.status_code == 429
    assert response.json() == {"detail": RATE_LIMIT_MESSAGE}


def test_rate_limit_response_does_not_leak_raw_error_details():
    for _ in range(_RATE_LIMIT_COUNT):
        client.post(f"{API_V1_PREFIX}/analyze-session", files=_garbage_files())

    response = client.post(f"{API_V1_PREFIX}/analyze-session", files=_garbage_files())

    body_text = response.text.lower()
    assert "traceback" not in body_text
    assert "exception" not in body_text
