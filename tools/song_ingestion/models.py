"""Lab veri modeli — `LabSong` ve sabit kümeleri.

Production `Song` modelinden (backend/app/services/recommendation.py) daha
zengindir: analiz meta verisi, timestamp'ler, review durumu, güven vb. tutar.
Production'a yalnızca bu modelin bir projeksiyonu (export.py) aktarılır.

Yalnızca standart kütüphane kullanır — Faz 0'da ağır bağımlılık olmadan test
edilebilir olması için.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field, fields

# ---- sabit kümeler (enum yerine frozenset; JSON/SQLite ile sürtünmesiz) ----

VOCAL_MODES = frozenset({"sung", "melodic_rap", "rap", "mixed", "unknown"})
SOURCE_TYPES = frozenset(
    {"singingcarrots", "published_score", "midi", "audio_analysis", "manual"}
)
REVIEW_STATUSES = frozenset({"pending", "approved", "rejected", "needs_review"})


@dataclass
class LabSong:
    """Katalogdaki tek bir şarkı kaydı.

    Aralık iki biçimde tutulur (bkz. K-064):
    - full_range: şarkıda gerçekten anlamlı biçimde kullanılan uç notalar
    - tessitura: sesin büyük bölümünde kaldığı temel bölge (öneri bunu önceler)

    Boundary notaların timestamp'i (detected_low/high_timestamp) review
    ekranında "o anı dinle" için tutulur.
    """

    id: str
    title: str
    artist: str
    language: str = "tr"
    genre: str = ""

    vocal_mode: str = "unknown"  # VOCAL_MODES

    full_range_low_midi: int | None = None
    full_range_high_midi: int | None = None
    full_range_low_note: str | None = None
    full_range_high_note: str | None = None

    tessitura_low_midi: int | None = None
    tessitura_high_midi: int | None = None
    tessitura_low_note: str | None = None
    tessitura_high_note: str | None = None

    range_semitones: int | None = None

    detected_low_timestamp: float | None = None  # saniye
    detected_high_timestamp: float | None = None  # saniye

    source_type: str = "audio_analysis"  # SOURCE_TYPES
    source_url: str | None = None

    analysis_method: str | None = None  # ör. "mel_band_roformer+rmvpe"
    analysis_version: str | None = None  # pipeline sürümü, tekrarlanabilirlik için
    analysis_confidence: float | None = None  # ÖLÇÜLEN kaliteden, sabit değil

    human_verified: bool = False
    review_status: str = "pending"  # REVIEW_STATUSES
    analysis_notes: str = ""

    # dahili
    content_hash: str | None = None  # aynı ses dosyası tekrar işlenmesin diye
    source_path: str | None = None  # yerel dosya yolu (review'da klip için)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def validate(self) -> None:
        """Sabit-küme alanlarının geçerli değer taşıdığını doğrular."""
        if self.vocal_mode not in VOCAL_MODES:
            raise ValueError(f"Geçersiz vocal_mode: {self.vocal_mode}")
        if self.source_type not in SOURCE_TYPES:
            raise ValueError(f"Geçersiz source_type: {self.source_type}")
        if self.review_status not in REVIEW_STATUSES:
            raise ValueError(f"Geçersiz review_status: {self.review_status}")

    @classmethod
    def field_names(cls) -> list[str]:
        return [f.name for f in fields(cls)]
