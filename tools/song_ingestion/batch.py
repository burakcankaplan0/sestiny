"""Toplu işleme: bir klasördeki ses dosyalarını sıraya alıp tek tek işler.

Tasarım (bkz. plan Q5):
- Klasör taranır, ses uzantılı dosyalar bulunur.
- Her dosyanın içerik hash'i alınır; katalogda zaten varsa ATLANIR (resume —
  yarıda kesilen batch tamamlananları tekrar işlemez).
- Her şarkı kendi try/except'inde işlenir; biri patlarsa batch DURMAZ, o kayıt
  needs_review olarak işaretlenir.
- Her şarkıdan sonra katalog commit edilir (upsert atomik) → checkpoint.
- Sonda özet döner: işlenen / başarılı / manuel gerekli / başarısız.

İşleme fonksiyonu (process_fn) dışarıdan alınır — böylece orkestrasyon, ağır
pipeline kurulmadan (Faz 0) sahte bir process_fn ile test edilebilir.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from .catalog import Catalog
from .decode import content_hash
from .ingest import pipeline
from .models import LabSong

AUDIO_EXTENSIONS = {".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg", ".opus", ".wma", ".aiff"}

ProcessFn = Callable[[Path], LabSong]


@dataclass
class BatchReport:
    processed: int = 0
    succeeded: int = 0
    needs_review: int = 0
    failed: int = 0
    skipped_already_done: int = 0

    def summary(self) -> str:
        return (
            f"{self.processed} işlendi / {self.succeeded} başarılı / "
            f"{self.needs_review} manuel kontrol / {self.failed} başarısız "
            f"({self.skipped_already_done} zaten yapılmış, atlandı)"
        )


def find_audio_files(folder: str | Path) -> list[Path]:
    root = Path(folder)
    return sorted(p for p in root.rglob("*") if p.suffix.lower() in AUDIO_EXTENSIONS)


def run(
    folder: str | Path,
    catalog: Catalog,
    process_fn: ProcessFn = pipeline.analyze_file,
) -> BatchReport:
    """Klasördeki tüm ses dosyalarını işler, kataloğa yazar, özet döndürür."""
    report = BatchReport()

    for audio_path in find_audio_files(folder):
        digest = content_hash(audio_path)
        if catalog.exists_by_hash(digest):
            report.skipped_already_done += 1
            continue

        report.processed += 1
        try:
            song = process_fn(audio_path)
            song.content_hash = digest
            song.source_path = str(audio_path)
            # Aralık üretilemeyen (rap vb.) veya düşük güvenli kayıtlar zaten
            # pipeline tarafından needs_review işaretlenmiş olabilir; buna saygı gösterilir.
            catalog.upsert(song)
            if song.review_status == "needs_review":
                report.needs_review += 1
            else:
                report.succeeded += 1
        except Exception as error:  # noqa: BLE001 - tek şarkı hatası batch'i durdurmamalı
            failed_song = LabSong(
                id=f"failed-{digest[:12]}",
                title=audio_path.stem,
                artist="",
                content_hash=digest,
                source_path=str(audio_path),
                review_status="needs_review",
                analysis_notes=f"İşleme hatası: {type(error).__name__}: {error}",
            )
            catalog.upsert(failed_song)
            report.failed += 1

    return report
