"""Ham (dönüştürülmüş ama normalize edilmemiş) ses sinyali üzerinde kayıt kalitesi kontrolü.

Normalizasyondan önce ölçüm yapılır (Karar K-009): aksi hâlde çok sessiz veya
bozuk bir kayıt yapay olarak iyi görünür ve kullanıcı hatalı bir sonuca güvenir.

Bu aşamada henüz pitch/perde analizi yapılmaz (Aşama 4'ün işi); yalnızca süre,
ses seviyesi, clipping ve sessizlik gibi perde bağımsız ölçütler değerlendirilir.
"""

from dataclasses import dataclass

import numpy as np

from app.core.config import (
    CLIPPING_REJECT_RATIO,
    CLIPPING_SAMPLE_THRESHOLD,
    CLIPPING_WARN_RATIO,
    MIN_RMS_WARN,
    MIN_TEST_DURATION_SECONDS,
    QUALITY_ACCEPT_SCORE_THRESHOLD,
    QUALITY_LABEL_GOOD_MIN,
    QUALITY_SCORE_WARNING_PENALTY,
    SILENCE_FRAME_MS,
    SILENCE_REJECT_RATIO,
    SILENCE_RMS_THRESHOLD,
    SILENCE_WARN_RATIO,
    TestId,
)


@dataclass(frozen=True)
class QualityMetrics:
    duration_seconds: float
    rms: float
    peak: float
    clipping_ratio: float
    silence_ratio: float


@dataclass(frozen=True)
class FileQualityResult:
    accepted: bool
    overall_score: int
    label: str
    warnings: list[str]
    duration_seconds: float


def compute_quality_metrics(samples: np.ndarray, sample_rate: int) -> QualityMetrics:
    """Süre, RMS, peak, clipping ve sessizlik oranını hesaplar."""
    duration_seconds = len(samples) / sample_rate if sample_rate > 0 else 0.0

    if len(samples) == 0:
        return QualityMetrics(duration_seconds=0.0, rms=0.0, peak=0.0, clipping_ratio=0.0, silence_ratio=1.0)

    rms = float(np.sqrt(np.mean(np.square(samples))))
    peak = float(np.max(np.abs(samples)))
    clipping_ratio = float(np.mean(np.abs(samples) >= CLIPPING_SAMPLE_THRESHOLD))
    silence_ratio = _compute_silence_ratio(samples, sample_rate)

    return QualityMetrics(
        duration_seconds=duration_seconds,
        rms=rms,
        peak=peak,
        clipping_ratio=clipping_ratio,
        silence_ratio=silence_ratio,
    )


def _compute_silence_ratio(samples: np.ndarray, sample_rate: int) -> float:
    """Kısa pencerelere bölüp her pencerenin RMS'ini eşikle karşılaştırarak sessizlik oranını bulur."""
    frame_length = max(1, int(sample_rate * SILENCE_FRAME_MS / 1000))
    frame_count = len(samples) // frame_length
    if frame_count == 0:
        # Kayıt bir pencereden bile kısa; tek pencere olarak değerlendir.
        window_rms = float(np.sqrt(np.mean(np.square(samples))))
        return 1.0 if window_rms < SILENCE_RMS_THRESHOLD else 0.0

    trimmed = samples[: frame_count * frame_length]
    frames = trimmed.reshape(frame_count, frame_length)
    frame_rms = np.sqrt(np.mean(np.square(frames), axis=1))
    silent_frames = np.sum(frame_rms < SILENCE_RMS_THRESHOLD)
    return float(silent_frames / frame_count)


def label_for_score(score: int) -> str:
    """0-100 skoru "iyi/orta/yetersiz" etiketine çevirir. Dosya kalitesi ve oturum
    genel kalitesi aynı eşikleri kullanır."""
    if score >= QUALITY_LABEL_GOOD_MIN:
        return "iyi"
    if score >= QUALITY_ACCEPT_SCORE_THRESHOLD:
        return "orta"
    return "yetersiz"


def evaluate_quality(test_id: TestId, metrics: QualityMetrics) -> FileQualityResult:
    """Ölçütleri eşiklerle karşılaştırıp kabul/ret kararı, skor, etiket ve uyarı listesi üretir."""
    warnings: list[str] = []
    score = 100
    hard_reject = False

    min_duration = MIN_TEST_DURATION_SECONDS[test_id]
    if metrics.duration_seconds < min_duration:
        warnings.append("Kayıt çok kısa görünüyor.")
        hard_reject = True
        score -= QUALITY_SCORE_WARNING_PENALTY

    if metrics.silence_ratio >= SILENCE_REJECT_RATIO:
        warnings.append("Ses seviyesi çok düşük. Mikrofona biraz daha yaklaşarak tekrar dene.")
        hard_reject = True
        score -= QUALITY_SCORE_WARNING_PENALTY
    elif metrics.silence_ratio >= SILENCE_WARN_RATIO or metrics.rms < MIN_RMS_WARN:
        warnings.append("Ses seviyesi düşük görünüyor. Mikrofona biraz daha yaklaşarak tekrar dene.")
        score -= QUALITY_SCORE_WARNING_PENALTY

    if metrics.clipping_ratio >= CLIPPING_REJECT_RATIO:
        warnings.append("Ses zaman zaman bozulmuş veya kesilmiş görünüyor.")
        hard_reject = True
        score -= QUALITY_SCORE_WARNING_PENALTY
    elif metrics.clipping_ratio >= CLIPPING_WARN_RATIO:
        warnings.append("Ses zaman zaman bozulmuş veya kesilmiş görünüyor.")
        score -= QUALITY_SCORE_WARNING_PENALTY

    score = max(0, score)
    accepted = not hard_reject and score >= QUALITY_ACCEPT_SCORE_THRESHOLD

    if not accepted and "Daha güvenilir sonuç için bu testi yeniden kaydet." not in warnings:
        warnings.append("Daha güvenilir sonuç için bu testi yeniden kaydet.")

    return FileQualityResult(
        accepted=accepted,
        overall_score=score,
        label=label_for_score(score),
        warnings=warnings,
        duration_seconds=metrics.duration_seconds,
    )
