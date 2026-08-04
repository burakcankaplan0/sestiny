"""Sağlık kontrolü endpoint'i.

Frontend, backend'e ulaşabildiğini bu endpoint ile doğrular.
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Sağlık kontrolü cevabı."""

    status: str
    message: str


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Backend'in ayakta olduğunu bildirir."""
    return HealthResponse(status="ok", message="Backend bağlantısı başarılı")
