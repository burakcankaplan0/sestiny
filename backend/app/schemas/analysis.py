"""Analiz oturumu isteği/cevabı için Pydantic şemaları."""

from typing import Literal

from pydantic import BaseModel, Field


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


class SongRecommendation(BaseModel):
    """Tek bir şarkı önerisi. `verified: false` olanlar demo veridir, gerçek şarkı değildir."""

    id: str
    title: str
    artist: str
    language: str
    genre: str
    difficulty: Literal["kolay", "orta", "zor"]
    min_note: str
    max_note: str
    match_score: int
    # Negatif: aşağıdan (daha pes), pozitif: yukarıdan denemek daha rahat olabilir. None: gerek yok.
    transposition_semitones: int | None
    verified: bool
    source_note: str
    # Türk makam müziğinde eserin sabit bir mutlak perdesi yoktur; icracı kendi
    # sesine uygun ahengi seçer (bkz. K-060). Bu tür eserlerde arayüz sayısal bir
    # yarı ton önerisi göstermez — "sesine uygun perdeden söylenir" der.
    freely_transposable: bool


class AnalyzeSessionResponse(BaseModel):
    """POST /api/v1/analyze-session cevabı.

    "accepted" durumu üç kaydın da analiz edilebilir kalitede olduğu anlamına
    gelir. `profile`, yalnızca oturum kabul edildiyse ve glide aralığı güvenilir
    şekilde belirlenebildiyse doldurulur; aksi hâlde `null`. `recommendations`
    aynı koşulda doldurulur; aksi hâlde boş liste (uydurma öneri yok).
    """

    session_id: str
    status: Literal["accepted", "rejected"]
    quality: QualitySummary
    speech: SpeechAnalysis
    sustained_vowel: SustainedVowelAnalysis
    glide: GlideAnalysis
    profile: ProfileSummary | None
    recommendations: list[SongRecommendation] = Field(default_factory=list)
