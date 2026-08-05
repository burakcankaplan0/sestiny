"""Analiz oturumu isteği/cevabı için Pydantic şemaları."""

from typing import Literal

from pydantic import BaseModel


class QualitySummary(BaseModel):
    """Oturum genelinde birleştirilmiş kayıt kalitesi özeti (üç testin en zayıfına göre)."""

    overall_score: int
    label: Literal["iyi", "orta", "yetersiz"]
    warnings: list[str]


class SpeechAnalysis(BaseModel):
    """Test 1 (Konuşma) sonucu."""

    accepted: bool
    warnings: list[str]
    duration_seconds: float
    median_f0_hz: float | None
    approximate_note: str | None
    pitch_variability_semitones: float | None
    voiced_ratio: float
    confidence: float


class SustainedVowelAnalysis(BaseModel):
    """Test 2 (Uzun "A" sesi) sonucu."""

    accepted: bool
    warnings: list[str]
    duration_seconds: float
    median_f0_hz: float | None
    approximate_note: str | None
    voiced_duration_seconds: float
    pitch_deviation_cents: float | None
    jump_count: int
    dropout_ratio: float
    stability_score: int
    stability_label: str
    confidence: float


class GlideAnalysis(BaseModel):
    """Test 3 (Kalından inceye kaydırma) sonucu."""

    accepted: bool
    warnings: list[str]
    duration_seconds: float
    observed_low_note: str | None
    observed_high_note: str | None
    observed_low_midi: int | None
    observed_high_midi: int | None
    range_semitones: int | None
    estimated_comfortable_low_note: str | None
    estimated_comfortable_high_note: str | None
    confidence: float


class ProfileSummary(BaseModel):
    """Tahmini ses profili — klasik ses türü sınıflandırması (bariton/soprano vb.) DEĞİLDİR."""

    label: str
    range_label: str
    summary: str


class AnalyzeSessionResponse(BaseModel):
    """POST /api/v1/analyze-session cevabı.

    "accepted" durumu üç kaydın da analiz edilebilir kalitede olduğu anlamına
    gelir. `profile`, yalnızca oturum kabul edildiyse ve glide aralığı güvenilir
    şekilde belirlenebildiyse doldurulur; aksi hâlde `null`. Şarkı önerileri
    henüz üretilmez — bu Aşama 6'nın işi.
    """

    session_id: str
    status: Literal["accepted", "rejected"]
    quality: QualitySummary
    speech: SpeechAnalysis
    sustained_vowel: SustainedVowelAnalysis
    glide: GlideAnalysis
    profile: ProfileSummary | None
