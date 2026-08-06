"""Hız sınırlama: CPU-yoğun analiz uç noktasını IP başına sınırlar.

Bellek içi sayaç kullanılır — Redis gibi harici bir servise ihtiyaç yok,
çünkü backend zaten tek process çalışıyor (bkz. README "Bilinen
sınırlamalar"). Eşik değeri app/core/config.py içinde tek yerde tutulur
(ANALYZE_SESSION_RATE_LIMIT).
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

RATE_LIMIT_MESSAGE = "Çok fazla istek gönderildi. Lütfen bir dakika sonra tekrar dene."


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Ham slowapi hatasını (limit detayları içerir) sızdırmadan Türkçe mesaj döner."""
    return JSONResponse(status_code=429, content={"detail": RATE_LIMIT_MESSAGE})
