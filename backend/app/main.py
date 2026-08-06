"""Sestiny backend uygulaması.

Çalıştırma (backend/ klasöründen):
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

from app.api import analysis, health
from app.core.config import API_V1_PREFIX, get_settings
from app.core.logging import configure_logging, get_logger
from app.core.rate_limit import limiter, rate_limit_exceeded_handler


def create_app() -> FastAPI:
    """Uygulamayı oluşturur ve yapılandırır."""
    settings = get_settings()
    configure_logging(settings.debug)
    logger = get_logger(__name__)

    application = FastAPI(
        title="Sestiny API",
        description="Tahmini ses profili analizi. Tıbbi veya profesyonel teşhis aracı değildir.",
        version="0.1.0",
    )

    # CORS yalnızca bilinen lokal frontend adreslerine açılır.
    # Production'da wildcard kullanılmaz — bkz. CLAUDE.md gizlilik kuralları.
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    # Hız sınırlama: yalnızca analiz uç noktasına uygulanır (bkz. app/api/analysis.py),
    # ama handler burada, uygulama genelinde kaydedilmeli.
    application.state.limiter = limiter
    application.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

    application.include_router(health.router, prefix=API_V1_PREFIX)
    application.include_router(analysis.router, prefix=API_V1_PREFIX)

    logger.info("Sestiny API hazır. İzinli origin'ler: %s", settings.allowed_origins_list)
    return application


app = create_app()
