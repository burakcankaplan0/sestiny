"""Song Ingestion Lab iskelet testleri — yalnızca standart kütüphane.

Ağır ses-ML bağımlılıkları GEREKTİRMEZ (Faz 0). Katalog CRUD/resume, batch
orkestrasyonu (hata yalıtımı + resume) ve export projeksiyonu test edilir.
"""

from pathlib import Path

import pytest

from tools.song_ingestion.batch import BatchReport, run
from tools.song_ingestion.catalog import Catalog
from tools.song_ingestion.export import export_approved, to_production_dict
from tools.song_ingestion.models import LabSong
from tools.song_ingestion.notes import hz_to_note_name, midi_to_note_name


@pytest.fixture
def catalog(tmp_path) -> Catalog:
    cat = Catalog(tmp_path / "test_catalog.db")
    yield cat
    cat.close()


def _song(**overrides) -> LabSong:
    defaults = dict(id="s1", title="Test", artist="Sanatçı")
    defaults.update(overrides)
    return LabSong(**defaults)


class TestNotes:
    def test_midi_to_note_name(self):
        assert midi_to_note_name(60) == "C4"
        assert midi_to_note_name(69) == "A4"

    def test_hz_to_note_name(self):
        assert hz_to_note_name(440.0) == "A4"


class TestCatalog:
    def test_upsert_and_get(self, catalog):
        catalog.upsert(_song(id="a", title="Şarkı A"))
        got = catalog.get("a")
        assert got is not None and got.title == "Şarkı A"

    def test_upsert_is_idempotent_update(self, catalog):
        catalog.upsert(_song(id="a", artist="İlk"))
        catalog.upsert(_song(id="a", artist="Güncel"))
        assert catalog.get("a").artist == "Güncel"
        assert len(catalog.all()) == 1

    def test_exists_by_hash_enables_resume(self, catalog):
        catalog.upsert(_song(id="a", content_hash="deadbeef"))
        assert catalog.exists_by_hash("deadbeef") is True
        assert catalog.exists_by_hash("yok") is False

    def test_list_by_status_and_set_status(self, catalog):
        catalog.upsert(_song(id="a", review_status="pending"))
        catalog.set_review_status("a", "approved", human_verified=True)
        assert catalog.list_by_status("pending") == []
        approved = catalog.list_by_status("approved")
        assert len(approved) == 1 and approved[0].human_verified is True

    def test_invalid_enum_rejected(self, catalog):
        with pytest.raises(ValueError):
            catalog.upsert(_song(vocal_mode="şarkı-değil"))

    def test_migration_preserves_existing_rows(self, tmp_path):
        db = tmp_path / "m.db"
        cat = Catalog(db)
        cat.upsert(_song(id="a"))
        cat.close()
        # Yeniden açmak _create_and_migrate'i tekrar çalıştırır; veri kaybolmamalı.
        cat2 = Catalog(db)
        assert cat2.get("a") is not None
        cat2.close()


def _fake_success(path: Path) -> LabSong:
    return LabSong(id=f"ok-{path.stem}", title=path.stem, artist="X", review_status="approved")


def _fake_needs_review(path: Path) -> LabSong:
    return LabSong(id=f"nr-{path.stem}", title=path.stem, artist="X", review_status="needs_review")


def _fake_crash(path: Path) -> LabSong:
    raise RuntimeError("analiz patladı")


def _make_audio_files(folder: Path, names: list[str]) -> None:
    for name in names:
        # İçerik farklı olsun ki content_hash farklı çıksın.
        (folder / name).write_bytes(name.encode() + b"-audio-bytes")


class TestBatch:
    def test_processes_all_and_reports(self, tmp_path, catalog):
        _make_audio_files(tmp_path, ["a.mp3", "b.wav", "c.flac"])
        report = run(tmp_path, catalog, process_fn=_fake_success)
        assert report.processed == 3 and report.succeeded == 3
        assert len(catalog.all()) == 3

    def test_one_crash_does_not_stop_batch(self, tmp_path, catalog):
        _make_audio_files(tmp_path, ["ok1.mp3", "bad.mp3", "ok2.mp3"])

        def process(path: Path) -> LabSong:
            return _fake_crash(path) if "bad" in path.stem else _fake_success(path)

        report = run(tmp_path, catalog, process_fn=process)
        assert report.processed == 3
        assert report.succeeded == 2
        assert report.failed == 1
        # Başarısız kayıt da katalogda, needs_review olarak durmalı.
        assert catalog.count_by_status().get("needs_review") == 1

    def test_needs_review_counted_separately(self, tmp_path, catalog):
        _make_audio_files(tmp_path, ["rap.mp3"])
        report = run(tmp_path, catalog, process_fn=_fake_needs_review)
        assert report.needs_review == 1 and report.succeeded == 0

    def test_resume_skips_already_done(self, tmp_path, catalog):
        _make_audio_files(tmp_path, ["a.mp3", "b.mp3"])
        run(tmp_path, catalog, process_fn=_fake_success)
        # İkinci çalıştırma: hepsi zaten hash'lenmiş, tekrar işlenmemeli.
        second = run(tmp_path, catalog, process_fn=_fake_crash)
        assert second.processed == 0
        assert second.skipped_already_done == 2

    def test_ignores_non_audio_files(self, tmp_path, catalog):
        _make_audio_files(tmp_path, ["song.mp3"])
        (tmp_path / "notes.txt").write_text("bu ses değil")
        report = run(tmp_path, catalog, process_fn=_fake_success)
        assert report.processed == 1


class TestExport:
    def test_only_approved_and_verified_are_exported(self, tmp_path, catalog):
        catalog.upsert(_song(id="a", review_status="approved", human_verified=True,
                             full_range_low_midi=48, full_range_high_midi=64))
        catalog.upsert(_song(id="b", review_status="approved", human_verified=False,
                             full_range_low_midi=48, full_range_high_midi=64))
        catalog.upsert(_song(id="c", review_status="pending", human_verified=True,
                             full_range_low_midi=48, full_range_high_midi=64))
        out = tmp_path / "export.json"
        count = export_approved(catalog, out)
        assert count == 1  # yalnızca a

    def test_production_dict_shape(self):
        song = _song(
            id="x", title="Deneme", artist="Sanatçı", language="tr", genre="pop",
            full_range_low_midi=45, full_range_high_midi=69,
            tessitura_low_midi=52, tessitura_high_midi=62,
            source_type="audio_analysis", source_url="file://x",
            analysis_method="roformer+rmvpe",
        )
        d = to_production_dict(song)
        assert d["min_midi"] == 45 and d["max_midi"] == 69
        assert d["tessitura_low_midi"] == 52 and d["tessitura_high_midi"] == 62
        assert d["verified"] is True
        assert "İnsan tarafından doğrulandı" in d["source_note"]
        assert d["difficulty"] == "zor"  # 24 yarı ton

    def test_exported_json_is_loadable_by_production_schema(self, tmp_path, catalog):
        """Export edilen JSON, production Song(**entry) ile hatasız yüklenmeli (geriye uyum)."""
        catalog.upsert(_song(id="a", review_status="approved", human_verified=True,
                             language="tr", genre="pop",
                             full_range_low_midi=48, full_range_high_midi=64,
                             tessitura_low_midi=52, tessitura_high_midi=60))
        out = tmp_path / "export.json"
        export_approved(catalog, out)

        import json as _json
        import sys

        backend_root = Path(__file__).resolve().parents[3] / "backend"
        sys.path.insert(0, str(backend_root))
        try:
            from app.services.recommendation import Song  # type: ignore

            records = _json.loads(out.read_text(encoding="utf-8"))
            songs = [Song(**entry) for entry in records]
            assert songs[0].tessitura_low_midi == 52
        finally:
            sys.path.remove(str(backend_root))
