"""Onaylı lab kayıtlarını Sestiny production JSON şemasına projekte eder.

Yalnızca `review_status == "approved"` VE `human_verified == True` kayıtlar
export edilir — dürüstlük kapısı budur. Çıktı, backend/app/data/ altındaki
diğer *_songs.json dosyalarıyla aynı şemadadır ve `load_songs()` ile okunur.

Zengin lab modeli → yalın production modeli projeksiyonu:
- min/max_midi  ← full_range
- tessitura_*   ← tessitura (öneri bunu önceler, K-064)
- source_tier=3 (ölçüm) — production güveni katman tablosundan gelir
- source_note   ← kaynak türü + URL + analiz yöntemi + "insan tarafından doğrulandı"

Yalnızca standart kütüphane — ağır bağımlılık gerektirmez.
"""

from __future__ import annotations

import json
from pathlib import Path

from .catalog import Catalog
from .models import LabSong

# K-048 ile aynı zorluk kuralı (aralık genişliğinden), production'la tutarlı.
DIFFICULTY_EASY_MAX = 13
DIFFICULTY_MEDIUM_MAX = 19

# Ölçümle elde edilen veri: production kaynak katmanı 3 (bkz. config.SOURCE_TIER_MEASURED).
PRODUCTION_SOURCE_TIER_MEASURED = 3


def _difficulty(span_semitones: int) -> str:
    if span_semitones <= DIFFICULTY_EASY_MAX:
        return "kolay"
    if span_semitones <= DIFFICULTY_MEDIUM_MAX:
        return "orta"
    return "zor"


def to_production_dict(song: LabSong) -> dict:
    """Bir onaylı LabSong'u production Song JSON kaydına çevirir."""
    span = (song.full_range_high_midi or 0) - (song.full_range_low_midi or 0)
    source_bits = [f"Kaynak türü: {song.source_type}"]
    if song.source_url:
        source_bits.append(f"URL: {song.source_url}")
    if song.analysis_method:
        source_bits.append(f"Analiz: {song.analysis_method}")
    source_bits.append("İnsan tarafından doğrulandı.")

    return {
        "id": song.id,
        "title": song.title,
        "artist": song.artist,
        "language": song.language,
        "genre": song.genre,
        "min_midi": song.full_range_low_midi,
        "max_midi": song.full_range_high_midi,
        "difficulty": _difficulty(span),
        "verified": True,
        "source_note": " ".join(source_bits),
        "optional_transposition_limit": None,
        "source_tier": PRODUCTION_SOURCE_TIER_MEASURED,
        "freely_transposable": False,
        "tessitura_low_midi": song.tessitura_low_midi,
        "tessitura_high_midi": song.tessitura_high_midi,
        "vocal_mode": song.vocal_mode,
    }


def export_approved(catalog: Catalog, output_path: str | Path) -> int:
    """Onaylı+doğrulanmış kayıtları production JSON'una yazar; kaç kayıt yazıldığını döndürür."""
    approved = [
        song
        for song in catalog.list_by_status("approved")
        if song.human_verified
        and song.full_range_low_midi is not None
        and song.full_range_high_midi is not None
    ]
    records = [to_production_dict(song) for song in approved]
    Path(output_path).write_text(
        json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return len(records)
