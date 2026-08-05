"""Tarayıcıdan gelen ses dosyalarını analiz için standart mono PCM dizisine çevirir.

Format kontrolü dosyayı gerçekten çözerek yapılır; MIME türüne veya dosya
uzantısına güvenilmez (bkz. CLAUDE.md güvenlik kuralları — "MIME türü tek başına
güvenilir kabul edilmemeli", "dosya uzantısına tek başına güvenilmemeli").
PyAV, ffmpeg'in ses/video kütüphanelerini içinde taşır; sisteme ayrıca FFmpeg
kurulması gerekmez (Karar K-007).
"""

import av
import numpy as np


class UnsupportedAudioError(Exception):
    """Yüklenen dosya geçerli/desteklenen bir ses formatı olarak çözümlenemedi."""


def decode_to_mono_array(file_path: str, target_sample_rate: int) -> tuple[np.ndarray, int]:
    """Dosyayı mono, float32, target_sample_rate'e yeniden örneklenmiş bir diziye çevirir.

    Dosya açılamıyorsa, içinde ses akışı yoksa veya çözümlenemiyorsa UnsupportedAudioError fırlatır.
    """
    try:
        container = av.open(file_path)
    except Exception as error:
        raise UnsupportedAudioError(f"Dosya açılamadı: {error}") from error

    try:
        stream = next((s for s in container.streams if s.type == "audio"), None)
        if stream is None:
            raise UnsupportedAudioError("Dosyada ses akışı bulunamadı.")

        resampler = av.AudioResampler(format="fltp", layout="mono", rate=target_sample_rate)
        chunks: list[np.ndarray] = []

        for packet in container.demux(stream):
            for frame in packet.decode():
                for resampled in resampler.resample(frame):
                    chunks.append(resampled.to_ndarray())

        # Resampler'ın iç arabelleğinde kalan son örnekleri de al.
        for resampled in resampler.resample(None):
            chunks.append(resampled.to_ndarray())
    except UnsupportedAudioError:
        raise
    except Exception as error:
        raise UnsupportedAudioError(f"Ses çözümlenemedi: {error}") from error
    finally:
        container.close()

    if not chunks:
        raise UnsupportedAudioError("Ses verisi çözümlenemedi.")

    samples = np.concatenate(chunks, axis=1).flatten().astype(np.float32)
    return samples, target_sample_rate
