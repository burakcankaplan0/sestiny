"""Üç test sonucundan basit, kesin olmayan bir "tahmini ses profili" oluşturur.

CLAUDE.md gereği bu bir klasik ses türü sınıflandırması (bariton/tenor/alto/
mezzo-soprano/soprano) DEĞİLDİR; yalnızca "merkez bölge" ve "aralık genişliği"
gibi kaba, açıklamalı kategorilerdir. Sınır değerleri bilimsel/klinik bir
standarda dayanmaz (bkz. core/config.py). Biyolojik cinsiyet tahmin edilmez.
"""

from dataclasses import dataclass

from app.core.config import (
    PROFILE_CENTER_LOW_MAX_MIDI,
    PROFILE_CENTER_LOW_MID_MAX_MIDI,
    PROFILE_CENTER_MID_HIGH_MAX_MIDI,
    PROFILE_CENTER_MID_MAX_MIDI,
    PROFILE_RANGE_NARROW_MAX_SEMITONES,
    PROFILE_RANGE_WIDE_MIN_SEMITONES,
)
from app.services.pitch_analysis import GlideAnalysis, SustainedVowelAnalysis

_CENTER_BUCKETS: list[tuple[float, str, str]] = [
    (PROFILE_CENTER_LOW_MAX_MIDI, "düşük", "düşük merkezli ses profili"),
    (PROFILE_CENTER_LOW_MID_MAX_MIDI, "orta-düşük", "orta-düşük merkezli ses profili"),
    (PROFILE_CENTER_MID_MAX_MIDI, "orta", "orta merkezli ses profili"),
    (PROFILE_CENTER_MID_HIGH_MAX_MIDI, "orta-yüksek", "orta-yüksek merkezli ses profili"),
]
_CENTER_HIGHEST = ("yüksek", "yüksek merkezli ses profili")

_STABILITY_PHRASES = {
    "stabil": "yüksekti",
    "orta düzeyde stabil": "orta düzeydeydi",
    "geliştirilebilir": "geliştirilebilir düzeydeydi",
}


@dataclass(frozen=True)
class ProfileResult:
    label: str
    range_label: str
    summary: str


def _center_labels(center_midi: float) -> tuple[str, str]:
    for max_midi, short, full in _CENTER_BUCKETS:
        if center_midi < max_midi:
            return short, full
    return _CENTER_HIGHEST


def _range_label(range_semitones: int) -> str:
    if range_semitones < PROFILE_RANGE_NARROW_MAX_SEMITONES:
        return "dar gözlemlenen aralık"
    if range_semitones < PROFILE_RANGE_WIDE_MIN_SEMITONES:
        return "orta genişlikte gözlemlenen aralık"
    return "geniş gözlemlenen aralık"


def build_profile(vowel: SustainedVowelAnalysis, glide: GlideAnalysis) -> ProfileResult | None:
    """Glide aralığı güvenilir şekilde belirlenemediyse profil üretmez (uydurma değer yok)."""
    if glide.observed_low_midi is None or glide.observed_high_midi is None:
        return None

    center_midi = (glide.observed_low_midi + glide.observed_high_midi) / 2
    short_center, full_label = _center_labels(center_midi)
    range_label = _range_label(glide.range_semitones or 0)
    stability_phrase = _STABILITY_PHRASES.get(vowel.stability_label, "belirsiz düzeydeydi")

    summary = (
        f"Kaydında {short_center} bölgede yoğunlaşan bir ses profili gözlemlendi. "
        f"Uzun ses testinde perde kararlılığın {stability_phrase}. "
        f"Kaydırma testinde yaklaşık {glide.observed_low_note}–{glide.observed_high_note} aralığı gözlemlendi. "
        "Bu değerler profesyonel bir ses türü teşhisi değildir ve mikrofon, ortam, teknik ve "
        "o anki ses durumundan etkilenebilir."
    )

    return ProfileResult(label=full_label, range_label=range_label, summary=summary)
