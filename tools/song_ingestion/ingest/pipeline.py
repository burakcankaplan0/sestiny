"""Tek bir ses dosyasını uçtan uca işleyip bir LabSong üretir.

decode → separate → pitch → segment(sung/rap) → range(+tessitura) → confidence.

Rap/spoken bir parçada güvenilir melodik aralık bulunamazsa: sayı ÜRETİLMEZ,
kayıt vocal_mode="rap", review_status="needs_review" olarak döner.

Aşama gövdeleri Faz 1'de dolacak; bu fonksiyon onları birleştiren sözleşmedir.
"""

from __future__ import annotations

from pathlib import Path

from ..models import LabSong

ANALYSIS_VERSION = "0.0.0-skeleton"


def analyze_file(
    file_path: str | Path,
    *,
    separation_model: str = "mel_band_roformer",
    pitch_model: str = "rmvpe",
) -> LabSong:
    """Bir ses dosyasını analiz edip LabSong döndürür. Faz 1'de doldurulacak.

    Faz 0'da bilinçli olarak NotImplementedError atar — batch orkestrasyonu
    (resume, hata yalıtımı) bu fonksiyondan bağımsız test edilebilir, çünkü
    batch.run() işleme fonksiyonunu dışarıdan alır (dependency injection).
    """
    raise NotImplementedError(
        "Analiz pipeline'ı Faz 1'de eklenecek (ayrıştırma + pitch modelleri)."
    )
