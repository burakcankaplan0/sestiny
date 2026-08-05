"""Analiz oturumu isteği/cevabı için Pydantic şemaları."""

from typing import Literal

from pydantic import BaseModel


class FileQualityReport(BaseModel):
    """Tek bir test kaydının kalite değerlendirmesi."""

    accepted: bool
    overall_score: int
    label: Literal["iyi", "orta", "yetersiz"]
    warnings: list[str]
    duration_seconds: float


class AnalyzeSessionResponse(BaseModel):
    """POST /api/v1/analyze-session cevabı.

    Bu aşamada yalnızca kayıt kalitesi değerlendirilir; pitch/perde analizi ve
    ses profili henüz üretilmez (bkz. Aşama 4/5). "accepted" durumu, üç kaydın
    da analiz edilebilir kalitede olduğu anlamına gelir — analiz sonucu değil.
    """

    session_id: str
    status: Literal["accepted", "rejected"]
    speech: FileQualityReport
    sustained_vowel: FileQualityReport
    glide: FileQualityReport
