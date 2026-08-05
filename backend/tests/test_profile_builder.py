"""profile_builder.build_profile testleri — kesin/tıbbi ifade kullanılmadığını da doğrular."""

from app.services.pitch_analysis import GlideAnalysis, SustainedVowelAnalysis
from app.services.profile_builder import build_profile

FORBIDDEN_PHRASES = ["kesin", "sağlıklı", "sağlıksız", "teşhis konuldu", "bariton", "tenor", "soprano"]


def _vowel(stability_label: str = "stabil") -> SustainedVowelAnalysis:
    return SustainedVowelAnalysis(
        median_f0_hz=150.0,
        approximate_note="D3",
        voiced_duration_seconds=5.0,
        pitch_deviation_cents=10.0,
        jump_count=0,
        dropout_ratio=0.0,
        stability_score=90,
        stability_label=stability_label,
        confidence=0.9,
    )


def _glide(low_midi: int = 43, high_midi: int = 64) -> GlideAnalysis:
    return GlideAnalysis(
        observed_low_note="G2",
        observed_high_note="E4",
        observed_low_midi=low_midi,
        observed_high_midi=high_midi,
        range_semitones=high_midi - low_midi,
        estimated_comfortable_low_note="A2",
        estimated_comfortable_high_note="D4",
        confidence=0.9,
    )


def test_no_glide_range_means_no_profile():
    """Glide aralığı belirlenemediyse profil uydurulmaz."""
    empty_glide = GlideAnalysis(
        observed_low_note=None,
        observed_high_note=None,
        observed_low_midi=None,
        observed_high_midi=None,
        range_semitones=None,
        estimated_comfortable_low_note=None,
        estimated_comfortable_high_note=None,
        confidence=0.0,
    )
    assert build_profile(_vowel(), empty_glide) is None


def test_low_range_gets_low_centered_label():
    profile = build_profile(_vowel(), _glide(low_midi=30, high_midi=40))
    assert profile is not None
    assert profile.label == "düşük merkezli ses profili"


def test_high_range_gets_high_centered_label():
    profile = build_profile(_vowel(), _glide(low_midi=68, high_midi=78))
    assert profile is not None
    assert profile.label == "yüksek merkezli ses profili"


def test_narrow_range_gets_narrow_label():
    profile = build_profile(_vowel(), _glide(low_midi=50, high_midi=55))
    assert profile is not None
    assert profile.range_label == "dar gözlemlenen aralık"


def test_wide_range_gets_wide_label():
    profile = build_profile(_vowel(), _glide(low_midi=40, high_midi=65))
    assert profile is not None
    assert profile.range_label == "geniş gözlemlenen aralık"


def test_summary_never_contains_diagnostic_or_classical_terms():
    """CLAUDE.md: kesin/tıbbi ifade ve klasik ses türü sınıflandırması yasak."""
    for stability_label in ("stabil", "orta düzeyde stabil", "geliştirilebilir"):
        profile = build_profile(_vowel(stability_label), _glide())
        assert profile is not None
        combined = f"{profile.label} {profile.range_label} {profile.summary}".lower()
        for forbidden in FORBIDDEN_PHRASES:
            assert forbidden not in combined, f"'{forbidden}' metinde bulunmamalı: {combined}"
        assert "teşhisi değildir" in profile.summary
