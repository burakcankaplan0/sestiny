"""Tek bir gerçek ses dosyasını Direct RMVPE pipeline'ıyla analiz eder.

Yalnızca lab aracı. Dosyayı production'a KOPYALAMAZ, production'a bağımlılık
EKLEMEZ, katalog/production'a veri YAZMAZ — sadece analiz edip rapor basar ve
iki uç bölge için kısa preview klipleri üretir (Git'e girmez).

Kullanım (lab venv):
    tools/song_ingestion/venv/bin/python -m tools.song_ingestion.analyze_file "/yol/sarki.mp3" [etiket]

`etiket` verilirse preview dosyaları o etiketle adlandırılır (5 şarkılık pilotta
klipler birbirini ezmesin diye). Örn: etiket "02" → low_extreme_preview_02.wav.

Not: mevcut eşikler DEĞİŞTİRİLMEZ; sonuç olduğu gibi raporlanır.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

# Uç nota preview'ının merkez etrafında alacağı yarım-pencere (saniye).
PREVIEW_HALF_WINDOW_SECONDS = 5.0
PREVIEW_DIR = Path(__file__).resolve().parent / "previews"
DECODE_SAMPLE_RATE = 44100


def _read_metadata(file_path: str) -> tuple[str | None, str | None]:
    """Dosya etiketlerinden (title, artist). Güvenilir bulunamazsa None — tahmin edilmez."""
    import av

    try:
        container = av.open(file_path)
    except Exception:
        return None, None
    try:
        meta = dict(container.metadata or {})
    finally:
        container.close()

    def pick(*keys: str) -> str | None:
        for key in keys:
            for candidate in (key, key.upper(), key.capitalize()):
                value = meta.get(candidate)
                if value and value.strip():
                    return value.strip()
        return None

    return pick("title"), pick("artist", "author", "album_artist")


def _write_preview(audio, sample_rate: int, center_seconds: float, name: str) -> Path | None:
    """center_seconds etrafında ±PREVIEW_HALF_WINDOW klip yazar (WAV). Yol döner."""
    import numpy as np
    import soundfile as sf

    if center_seconds is None:
        return None
    start = max(0, int((center_seconds - PREVIEW_HALF_WINDOW_SECONDS) * sample_rate))
    end = min(len(audio), int((center_seconds + PREVIEW_HALF_WINDOW_SECONDS) * sample_rate))
    if end <= start:
        return None
    PREVIEW_DIR.mkdir(exist_ok=True)
    out_path = PREVIEW_DIR / f"{name}.wav"
    sf.write(str(out_path), np.asarray(audio[start:end], dtype="float32"), sample_rate)
    return out_path


def main() -> int:
    if len(sys.argv) not in (2, 3):
        print('Kullanım: python -m tools.song_ingestion.analyze_file "/yol/sarki.mp3" [etiket]', file=sys.stderr)
        return 1
    file_path = sys.argv[1]
    label = sys.argv[2] if len(sys.argv) == 3 else None
    if not Path(file_path).is_file():
        print(f"Dosya bulunamadı: {file_path}", file=sys.stderr)
        return 1

    from tools.song_ingestion.decode import decode_to_mono
    from tools.song_ingestion.ingest import pitch
    from tools.song_ingestion.ingest.engine import analyze_audio

    title, artist = _read_metadata(file_path)
    samples, sr = decode_to_mono(file_path, DECODE_SAMPLE_RATE)
    duration = len(samples) / sr

    # Model yükleme süresini inference'tan ayır: modeli önceden ısıt.
    t0 = time.perf_counter()
    pitch._get_rmvpe()
    model_load_seconds = time.perf_counter() - t0

    result = analyze_audio(samples, sr)  # rmvpe_seconds artık yalnızca inference

    suffix = f"_{label}" if label else ""
    low_preview = _write_preview(samples, sr, result.low_note_timestamp, f"low_extreme_preview{suffix}")
    high_preview = _write_preview(samples, sr, result.high_note_timestamp, f"high_extreme_preview{suffix}")

    low_seg = _segment_at(result, result.full_range_low_midi)
    high_seg = _segment_at(result, result.full_range_high_midi)
    total_valid = sum(s.duration for s in result.segments)
    tess_cov = _tessitura_coverage(result)

    def fmt(v):
        return "—" if v is None else v

    print("=" * 60)
    print(f"Dosya: {Path(file_path).name}")
    print(f"Şarkı adı (metadata): {fmt(title)}")
    print(f"Sanatçı (metadata): {fmt(artist)}")
    print(f"Süre: {duration:.1f} sn")
    print()
    print("FULL RANGE")
    print(f"  En düşük nota: {fmt(result.full_range_low_note)} (MIDI {fmt(result.full_range_low_midi)})")
    print(f"    timestamp: {fmt(result.low_note_timestamp)} sn | destek süresi: {fmt(result.low_note_duration)} sn"
          f" | median confidence: {low_seg.median_confidence if low_seg else '—'}")
    print(f"  En yüksek nota: {fmt(result.full_range_high_note)} (MIDI {fmt(result.full_range_high_midi)})")
    print(f"    timestamp: {fmt(result.high_note_timestamp)} sn | destek süresi: {fmt(result.high_note_duration)} sn"
          f" | median confidence: {high_seg.median_confidence if high_seg else '—'}")
    print()
    print("TESSITURA")
    print(f"  Alt: {fmt(result.tessitura_low_note)} | Üst: {fmt(result.tessitura_high_note)}")
    if result.tessitura_low_midi is not None:
        print(f"  Genişlik: {result.tessitura_high_midi - result.tessitura_low_midi} yarı ton")
    print(f"  Kapsanan geçerli vokal süresi oranı: {tess_cov}")
    print()
    print("ANALİZ KALİTESİ")
    print(f"  analysis_confidence: {result.analysis_confidence}")
    print(f"  average RMVPE confidence: {result.average_pitch_confidence}")
    print(f"  voiced_frame_ratio: {result.voiced_frame_ratio}")
    print(f"  discarded_frame_ratio: {result.discarded_frame_ratio}")
    print(f"  octave_jump_ratio: {result.octave_jump_ratio}")
    print(f"  toplam kabul edilen segment: {len(result.segments)} | toplam geçerli vokal süresi: {round(total_valid,1)} sn")
    print(f"  review_status: {result.review_status}")
    print(f"  needs_review_reason: {result.needs_review_reason or '—'}")
    print()
    print("PERFORMANS")
    print(f"  model yükleme: {round(model_load_seconds,3)} sn")
    print(f"  inference (rmvpe): {result.rmvpe_seconds} sn")
    print(f"  post-processing: {result.postprocessing_seconds} sn")
    print(f"  toplam (yükleme hariç): {result.total_seconds} sn")
    print()
    print("UÇ BÖLGE PREVIEW (Git'e girmez; dinleyip değerlendir):")
    print(f"  low_extreme_preview:  {low_preview if low_preview else '— (uç nota yok)'}")
    print(f"  high_extreme_preview: {high_preview if high_preview else '— (uç nota yok)'}")
    print("=" * 60)
    return 0


def _segment_at(result, midi):
    if midi is None:
        return None
    matches = [s for s in result.segments if s.midi == midi]
    return max(matches, key=lambda s: s.duration) if matches else None


def _tessitura_coverage(result) -> str:
    """Tessitura bandının kapsadığı geçerli vokal süresi oranı (yaklaşık)."""
    if result.tessitura_low_midi is None:
        return "—"
    total = sum(s.duration for s in result.segments)
    if total <= 0:
        return "—"
    covered = sum(
        s.duration for s in result.segments
        if result.tessitura_low_midi <= s.midi <= result.tessitura_high_midi
    )
    return f"%{round(100 * covered / total)}"


if __name__ == "__main__":
    raise SystemExit(main())
