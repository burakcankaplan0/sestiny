"""SQLite tabanlı şarkı kataloğu.

Neden SQLite (düz JSON değil): batch işleme yarıda kesilebilir; her şarkıdan
sonra atomik commit ile "işlendi mi" durumu kalıcı olur ve resume mümkün olur.
Review durumu (pending/approved/...) da aynı yerde tutulur. Production bu
dosyayı HİÇ okumaz — yalnızca export.py'nin ürettiği JSON'u okur.

Yalnızca standart kütüphane (sqlite3) — Faz 0'da ağır bağımlılık olmadan test
edilebilir.
"""

from __future__ import annotations

import sqlite3
from dataclasses import asdict
from pathlib import Path

from .models import LabSong

DEFAULT_DB_PATH = Path(__file__).resolve().parent / "catalog.db"


class Catalog:
    """LabSong kayıtlarını saklayan ince bir SQLite sarmalayıcı.

    Şema, LabSong alanlarından türetilir — model büyüdükçe migrate() yeni
    kolonları ekler (SQLite ALTER TABLE ADD COLUMN), böylece mevcut katalog
    kaybolmaz.
    """

    def __init__(self, db_path: Path | str = DEFAULT_DB_PATH) -> None:
        self.db_path = str(db_path)
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._create_and_migrate()

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "Catalog":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    # ---- şema ----

    def _create_and_migrate(self) -> None:
        columns = LabSong.field_names()
        # id birincil anahtar; geri kalan alanlar esnek tiplerde (SQLite dinamik).
        col_defs = ", ".join(
            f"{name} TEXT PRIMARY KEY" if name == "id" else f"{name}" for name in columns
        )
        self._conn.execute(f"CREATE TABLE IF NOT EXISTS songs ({col_defs})")
        # Model sonradan alan kazanırsa eksik kolonları ekle (mevcut veriyi korur).
        existing = {row["name"] for row in self._conn.execute("PRAGMA table_info(songs)")}
        for name in columns:
            if name not in existing:
                self._conn.execute(f"ALTER TABLE songs ADD COLUMN {name}")
        self._conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON songs(review_status)")
        self._conn.execute("CREATE INDEX IF NOT EXISTS idx_hash ON songs(content_hash)")
        self._conn.commit()

    # ---- yazma ----

    def upsert(self, song: LabSong) -> None:
        """Kaydı ekler veya (aynı id ile) günceller."""
        song.validate()
        data = asdict(song)
        columns = list(data.keys())
        placeholders = ", ".join(["?"] * len(columns))
        updates = ", ".join(f"{c}=excluded.{c}" for c in columns if c != "id")
        self._conn.execute(
            f"INSERT INTO songs ({', '.join(columns)}) VALUES ({placeholders}) "
            f"ON CONFLICT(id) DO UPDATE SET {updates}",
            [data[c] for c in columns],
        )
        self._conn.commit()

    def set_review_status(self, song_id: str, status: str, human_verified: bool | None = None) -> None:
        if status not in {"pending", "approved", "rejected", "needs_review"}:
            raise ValueError(f"Geçersiz review_status: {status}")
        if human_verified is None:
            self._conn.execute("UPDATE songs SET review_status=? WHERE id=?", (status, song_id))
        else:
            self._conn.execute(
                "UPDATE songs SET review_status=?, human_verified=? WHERE id=?",
                (status, int(human_verified), song_id),
            )
        self._conn.commit()

    # ---- okuma ----

    def _row_to_song(self, row: sqlite3.Row) -> LabSong:
        data = {key: row[key] for key in row.keys()}
        # SQLite bool'ları int olarak saklar; modele geri çevir.
        data["human_verified"] = bool(data.get("human_verified"))
        return LabSong(**data)

    def get(self, song_id: str) -> LabSong | None:
        row = self._conn.execute("SELECT * FROM songs WHERE id=?", (song_id,)).fetchone()
        return self._row_to_song(row) if row else None

    def exists_by_hash(self, content_hash: str) -> bool:
        """Aynı ses dosyası (içerik hash'i) daha önce işlendi mi — resume için."""
        row = self._conn.execute(
            "SELECT 1 FROM songs WHERE content_hash=? LIMIT 1", (content_hash,)
        ).fetchone()
        return row is not None

    def list_by_status(self, status: str) -> list[LabSong]:
        rows = self._conn.execute(
            "SELECT * FROM songs WHERE review_status=? ORDER BY updated_at", (status,)
        ).fetchall()
        return [self._row_to_song(r) for r in rows]

    def all(self) -> list[LabSong]:
        rows = self._conn.execute("SELECT * FROM songs ORDER BY updated_at").fetchall()
        return [self._row_to_song(r) for r in rows]

    def count_by_status(self) -> dict[str, int]:
        rows = self._conn.execute(
            "SELECT review_status, COUNT(*) AS n FROM songs GROUP BY review_status"
        ).fetchall()
        return {row["review_status"]: row["n"] for row in rows}
