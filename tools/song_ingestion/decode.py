"""Ses dosyasını standart mono float diziye çevirir + içerik hash'i üretir.

Çözme mantığı backend/app/services/audio_conversion.py ile aynı yaklaşımı izler
(PyAV, MIME/uzantıya güvenmez, gerçek çözümlemeyle doğrular). PyAV (`av`) ağır
bir bağımlılık olmadığı için fonksiyon içinde lazy import edilir — paket, av
kurulu olmadan da import edilebilsin (Faz 0).
"""

from __future__ import annotations

import hashlib
from pathlib import Path

# Analiz için hedef örnekleme oranı. Vokal F0 en fazla ~1.1 kHz; 44.1 kHz
# ayrıştırma modelleri için standart, pitch için fazlasıyla yeterli.
TARGET_SAMPLE_RATE = 44100


def content_hash(file_path: str | Path) -> str:
    """Dosya içeriğinin SHA-256'sı — aynı ses tekrar işlenmesin diye (resume)."""
    digest = hashlib.sha256()
    with open(file_path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def decode_to_mono(file_path: str | Path, target_sample_rate: int = TARGET_SAMPLE_RATE):
    """Dosyayı mono, float32, target_sample_rate diziye çevirir.

    Dönüş: (samples: np.ndarray, sample_rate: int). Çözülemezse ValueError.
    """
    import av  # lazy: ağır değil ama Faz 0'da kurulu olmayabilir
    import numpy as np

    try:
        container = av.open(str(file_path))
    except Exception as error:  # noqa: BLE001 - dış kütüphane çeşitli hatalar atar
        raise ValueError(f"Dosya açılamadı: {error}") from error

    try:
        stream = next((s for s in container.streams if s.type == "audio"), None)
        if stream is None:
            raise ValueError("Dosyada ses akışı yok.")
        resampler = av.AudioResampler(format="fltp", layout="mono", rate=target_sample_rate)
        chunks: list = []
        for packet in container.demux(stream):
            for frame in packet.decode():
                for resampled in resampler.resample(frame):
                    chunks.append(resampled.to_ndarray())
        for resampled in resampler.resample(None):
            chunks.append(resampled.to_ndarray())
    finally:
        container.close()

    if not chunks:
        raise ValueError("Ses verisi çözülemedi.")
    samples = np.concatenate(chunks, axis=1).flatten().astype(np.float32)
    return samples, target_sample_rate
