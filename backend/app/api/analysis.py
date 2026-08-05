"""Ses kaydı yükleme ve kalite değerlendirme endpoint'i."""

import os
import tempfile
import uuid

from fastapi import APIRouter, HTTPException, UploadFile

from app.core.config import TARGET_SAMPLE_RATE, TestId, get_settings
from app.core.logging import get_logger
from app.schemas.analysis import AnalyzeSessionResponse, FileQualityReport
from app.services.audio_conversion import UnsupportedAudioError, decode_to_mono_array
from app.services.audio_quality import compute_quality_metrics, evaluate_quality

router = APIRouter(tags=["analysis"])
logger = get_logger(__name__)

# Dosya okuma bu boyutlarda parça parça yapılır; tek seferde tüm dosyayı belleğe almamak için.
UPLOAD_CHUNK_BYTES = 1024 * 1024


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


def _evaluate_file(path: str, test_id: TestId) -> FileQualityReport:
    try:
        samples, sample_rate = decode_to_mono_array(path, TARGET_SAMPLE_RATE)
    except UnsupportedAudioError:
        return FileQualityReport(
            accepted=False,
            overall_score=0,
            label="yetersiz",
            warnings=["Ses formatı desteklenmiyor. Kaydı yeniden oluşturmayı dene."],
            duration_seconds=0.0,
        )

    metrics = compute_quality_metrics(samples, sample_rate)
    result = evaluate_quality(test_id, metrics)
    return FileQualityReport(
        accepted=result.accepted,
        overall_score=result.overall_score,
        label=result.label,
        warnings=result.warnings,
        duration_seconds=result.duration_seconds,
    )


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
        reports: dict[TestId, FileQualityReport] = {}
        for test_id, upload in uploads.items():
            path = await _save_upload_to_temp_file(upload, settings.max_upload_bytes)
            temp_paths.append(path)
            reports[test_id] = _evaluate_file(path, test_id)

        session_id = str(uuid.uuid4())
        all_accepted = all(report.accepted for report in reports.values())

        # Ses içeriği veya dosya yolu loglanmaz — yalnızca oturum kimliği ve sonuç.
        logger.info("Analiz oturumu değerlendirildi: session_id=%s kabul=%s", session_id, all_accepted)

        return AnalyzeSessionResponse(
            session_id=session_id,
            status="accepted" if all_accepted else "rejected",
            speech=reports["speech"],
            sustained_vowel=reports["sustained_vowel"],
            glide=reports["glide"],
        )
    finally:
        # Analiz bitince (başarılı ya da başarısız) geçici ses dosyaları her zaman silinir.
        for path in temp_paths:
            if os.path.exists(path):
                os.remove(path)
