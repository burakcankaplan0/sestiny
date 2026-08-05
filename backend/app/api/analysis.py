"""Ses kaydı yükleme, kalite değerlendirme, pitch analizi ve tahmini profil endpoint'i."""

import os
import tempfile
import uuid

import numpy as np
from fastapi import APIRouter, HTTPException, UploadFile

from app.core.config import TARGET_SAMPLE_RATE, TestId, get_settings
from app.core.logging import get_logger
from app.schemas.analysis import (
    AnalyzeSessionResponse,
    GlideAnalysis,
    ProfileSummary,
    QualitySummary,
    SongRecommendation,
    SpeechAnalysis,
    SustainedVowelAnalysis,
)
from app.services import pitch_analysis
from app.services.audio_conversion import UnsupportedAudioError, decode_to_mono_array
from app.services.audio_quality import FileQualityResult, compute_quality_metrics, evaluate_quality, label_for_score
from app.services.music_theory import midi_to_note_name
from app.services.profile_builder import build_profile
from app.services.recommendation import SongRecommendation as RecommendationResult
from app.services.recommendation import get_recommendations

router = APIRouter(tags=["analysis"])
logger = get_logger(__name__)

# Dosya okuma bu boyutlarda parça parça yapılır; tek seferde tüm dosyayı belleğe almamak için.
UPLOAD_CHUNK_BYTES = 1024 * 1024

# Kalite özetindeki uyarılara hangi testten geldiğini belirtmek için eklenen önek.
TEST_DISPLAY_NAMES: dict[TestId, str] = {
    "speech": "Konuşma testi",
    "sustained_vowel": 'Uzun "A" testi',
    "glide": "Kaydırma testi",
}

UNSUPPORTED_FORMAT_WARNING = "Ses formatı desteklenmiyor. Kaydı yeniden oluşturmayı dene."


async def _save_upload_to_temp_file(upload: UploadFile, max_bytes: int) -> str:
    """Yüklenen dosyayı güvenli, rastgele adlı bir geçici dosyaya yazar.

    Boyut sınırı aşılırsa dosyayı siler ve 413 fırlatır — büyük bir dosyayı
    tamamen belleğe/diske yazmadan önce erken keser.
    """
    fd, path = tempfile.mkstemp(prefix="sestiny_", suffix=".upload")
    total_bytes = 0
    try:
        with os.fdopen(fd, "wb") as destination:
            while True:
                chunk = await upload.read(UPLOAD_CHUNK_BYTES)
                if not chunk:
                    break
                total_bytes += len(chunk)
                if total_bytes > max_bytes:
                    raise HTTPException(status_code=413, detail="Dosya boyutu sınırı aşıldı.")
                destination.write(chunk)
    except Exception:
        os.remove(path)
        raise
    finally:
        await upload.close()
    return path


def _decode_and_evaluate_quality(
    path: str, test_id: TestId
) -> tuple[FileQualityResult, tuple[np.ndarray, int] | None]:
    """Dosyayı çözer ve kalitesini değerlendirir.

    Kalite kabul edilmişse (samples, sample_rate) döner; aksi hâlde pitch analizi
    hiç denenmez — kötü bir kayıt üzerinde anlamsız sayılar üretmemek için.
    """
    try:
        samples, sample_rate = decode_to_mono_array(path, TARGET_SAMPLE_RATE)
    except UnsupportedAudioError:
        quality = FileQualityResult(
            accepted=False,
            overall_score=0,
            label="yetersiz",
            warnings=[UNSUPPORTED_FORMAT_WARNING],
            duration_seconds=0.0,
        )
        return quality, None

    metrics = compute_quality_metrics(samples, sample_rate)
    quality = evaluate_quality(test_id, metrics)
    decoded = (samples, sample_rate) if quality.accepted else None
    return quality, decoded


def _combine_quality(reports: dict[TestId, FileQualityResult]) -> QualitySummary:
    """Üç testin en zayıfını temel alan oturum geneli kalite özeti.

    Uyarılar hangi testten geldiği belirtilerek listelenir; aksi hâlde kullanıcı
    hangi kaydı yeniden yapması gerektiğini anlayamaz.
    """
    overall_score = min(report.overall_score for report in reports.values())
    warnings: list[str] = []
    for test_id, report in reports.items():
        for warning in report.warnings:
            warnings.append(f"{TEST_DISPLAY_NAMES[test_id]}: {warning}")

    return QualitySummary(overall_score=overall_score, label=label_for_score(overall_score), warnings=warnings)


@router.post("/analyze-session", response_model=AnalyzeSessionResponse)
async def analyze_session(
    speech: UploadFile,
    sustained_vowel: UploadFile,
    glide: UploadFile,
) -> AnalyzeSessionResponse:
    settings = get_settings()
    uploads: dict[TestId, UploadFile] = {
        "speech": speech,
        "sustained_vowel": sustained_vowel,
        "glide": glide,
    }

    temp_paths: list[str] = []
    try:
        quality_reports: dict[TestId, FileQualityResult] = {}
        decoded_by_test: dict[TestId, tuple[np.ndarray, int] | None] = {}

        for test_id, upload in uploads.items():
            path = await _save_upload_to_temp_file(upload, settings.max_upload_bytes)
            temp_paths.append(path)
            quality, decoded = _decode_and_evaluate_quality(path, test_id)
            quality_reports[test_id] = quality
            decoded_by_test[test_id] = decoded

        # Pitch analizi yalnızca kalitesi kabul edilen dosyalar için çalıştırılır
        # (bkz. Karar K-031) — kötü bir kayıt üzerinde uydurma sonuç üretilmez.
        speech_result = (
            pitch_analysis.analyze_speech(*decoded_by_test["speech"]) if decoded_by_test["speech"] else None
        )
        vowel_result = (
            pitch_analysis.analyze_sustained_vowel(*decoded_by_test["sustained_vowel"])
            if decoded_by_test["sustained_vowel"]
            else None
        )
        glide_result = (
            pitch_analysis.analyze_glide(*decoded_by_test["glide"]) if decoded_by_test["glide"] else None
        )

        session_id = str(uuid.uuid4())
        all_accepted = all(report.accepted for report in quality_reports.values())

        # Ses içeriği veya dosya yolu loglanmaz — yalnızca oturum kimliği ve sonuç.
        logger.info("Analiz oturumu değerlendirildi: session_id=%s kabul=%s", session_id, all_accepted)

        profile = None
        if all_accepted and vowel_result is not None and glide_result is not None:
            profile_result = build_profile(vowel_result, glide_result)
            if profile_result is not None:
                profile = ProfileSummary(
                    label=profile_result.label,
                    range_label=profile_result.range_label,
                    summary=profile_result.summary,
                )

        # Şarkı önerileri, tahmini rahat bölge güvenilir şekilde belirlenebildiyse üretilir;
        # aksi hâlde boş liste döner — uydurma öneri yapılmaz.
        recommendations: list[SongRecommendation] = []
        if (
            all_accepted
            and glide_result is not None
            and glide_result.estimated_comfortable_low_midi is not None
            and glide_result.estimated_comfortable_high_midi is not None
        ):
            recommendations = [
                _recommendation_schema(item)
                for item in get_recommendations(
                    glide_result.estimated_comfortable_low_midi,
                    glide_result.estimated_comfortable_high_midi,
                )
            ]

        return AnalyzeSessionResponse(
            session_id=session_id,
            status="accepted" if all_accepted else "rejected",
            quality=_combine_quality(quality_reports),
            speech=_speech_schema(quality_reports["speech"], speech_result),
            sustained_vowel=_vowel_schema(quality_reports["sustained_vowel"], vowel_result),
            glide=_glide_schema(quality_reports["glide"], glide_result),
            profile=profile,
            recommendations=recommendations,
        )
    finally:
        # Analiz bitince (başarılı ya da başarısız) geçici ses dosyaları her zaman silinir.
        for path in temp_paths:
            if os.path.exists(path):
                os.remove(path)


def _speech_schema(quality: FileQualityResult, result: pitch_analysis.SpeechAnalysis | None) -> SpeechAnalysis:
    if result is None:
        return SpeechAnalysis(
            accepted=quality.accepted,
            warnings=quality.warnings,
            duration_seconds=quality.duration_seconds,
            median_f0_hz=None,
            approximate_note=None,
            pitch_variability_semitones=None,
            voiced_ratio=0.0,
            confidence=0.0,
        )
    return SpeechAnalysis(
        accepted=quality.accepted,
        warnings=quality.warnings,
        duration_seconds=quality.duration_seconds,
        median_f0_hz=result.median_f0_hz,
        approximate_note=result.approximate_note,
        pitch_variability_semitones=result.pitch_variability_semitones,
        voiced_ratio=result.voiced_ratio,
        confidence=result.confidence,
    )


def _vowel_schema(
    quality: FileQualityResult, result: pitch_analysis.SustainedVowelAnalysis | None
) -> SustainedVowelAnalysis:
    if result is None:
        return SustainedVowelAnalysis(
            accepted=quality.accepted,
            warnings=quality.warnings,
            duration_seconds=quality.duration_seconds,
            median_f0_hz=None,
            approximate_note=None,
            voiced_duration_seconds=0.0,
            pitch_deviation_cents=None,
            jump_count=0,
            dropout_ratio=1.0,
            stability_score=0,
            stability_label="geliştirilebilir",
            confidence=0.0,
        )
    return SustainedVowelAnalysis(
        accepted=quality.accepted,
        warnings=quality.warnings,
        duration_seconds=quality.duration_seconds,
        median_f0_hz=result.median_f0_hz,
        approximate_note=result.approximate_note,
        voiced_duration_seconds=result.voiced_duration_seconds,
        pitch_deviation_cents=result.pitch_deviation_cents,
        jump_count=result.jump_count,
        dropout_ratio=result.dropout_ratio,
        stability_score=result.stability_score,
        stability_label=result.stability_label,
        confidence=result.confidence,
    )


def _recommendation_schema(item: RecommendationResult) -> SongRecommendation:
    """recommendation.SongRecommendation'ı API şemasına çevirir; nota adları MIDI'den türetilir."""
    song = item.song
    return SongRecommendation(
        id=song.id,
        title=song.title,
        artist=song.artist,
        language=song.language,
        genre=song.genre,
        difficulty=song.difficulty,
        min_note=midi_to_note_name(song.min_midi),
        max_note=midi_to_note_name(song.max_midi),
        match_score=item.match_score,
        transposition_semitones=item.transposition_semitones,
        verified=song.verified,
        source_note=song.source_note,
    )


def _glide_schema(quality: FileQualityResult, result: pitch_analysis.GlideAnalysis | None) -> GlideAnalysis:
    if result is None:
        return GlideAnalysis(
            accepted=quality.accepted,
            warnings=quality.warnings,
            duration_seconds=quality.duration_seconds,
            observed_low_note=None,
            observed_high_note=None,
            observed_low_midi=None,
            observed_high_midi=None,
            range_semitones=None,
            estimated_comfortable_low_note=None,
            estimated_comfortable_high_note=None,
            confidence=0.0,
        )
    return GlideAnalysis(
        accepted=quality.accepted,
        warnings=quality.warnings,
        duration_seconds=quality.duration_seconds,
        observed_low_note=result.observed_low_note,
        observed_high_note=result.observed_high_note,
        observed_low_midi=result.observed_low_midi,
        observed_high_midi=result.observed_high_midi,
        range_semitones=result.range_semitones,
        estimated_comfortable_low_note=result.estimated_comfortable_low_note,
        estimated_comfortable_high_note=result.estimated_comfortable_high_note,
        confidence=result.confidence,
    )
