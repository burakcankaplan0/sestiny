"""Pipeline B benchmark: Direct RMVPE vs (vocal separation → RMVPE), yan yana.

Amaç: "Direct RMVPE'nin yanlışlıkla yakaladığı bas/enstrüman notaları vocals
stem'de kayboluyor mu?" Aynı orijinal dosya iki yolla analiz edilir; mevcut
KİLİTLİ segmentasyon eşikleri değişmeden kullanılır. Production'a hiçbir şey
yazılmaz; katalog değişmez.

Kullanım (lab venv):
    tools/song_ingestion/venv/bin/python -m tools.song_ingestion.benchmark_separation "/yol/sarki.mp3" <etiket>
"""

from __future__ import annotations

import resource
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf

from tools.song_ingestion.decode import content_hash, decode_to_mono
from tools.song_ingestion.ingest.engine import analyze_audio
from tools.song_ingestion.ingest.separate import SEPARATION_MODEL, separate_vocals_stem

DECODE_SR = 44100
PREVIEW_HALF_WINDOW_SECONDS = 5.0
PREVIEW_DIR = Path(__file__).resolve().parent / "previews"
STEM_CACHE = Path(__file__).resolve().parent / "stem_cache"


def _peak_ram_mb() -> float:
    # macOS ru_maxrss bayt cinsindendir.
    return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6, 1)


def _write_preview(audio, sr, center, name) -> Path | None:
    if center is None:
        return None
    start = max(0, int((center - PREVIEW_HALF_WINDOW_SECONDS) * sr))
    end = min(len(audio), int((center + PREVIEW_HALF_WINDOW_SECONDS) * sr))
    if end <= start:
        return None
    PREVIEW_DIR.mkdir(exist_ok=True)
    out = PREVIEW_DIR / f"{name}.wav"
    sf.write(str(out), np.asarray(audio[start:end], dtype="float32"), sr)
    return out


def _fmt_extremes(result) -> str:
    return (
        f"low {result.full_range_low_note}({result.full_range_low_midi}) "
        f"@{result.low_note_timestamp}s d={result.low_note_duration}s  |  "
        f"high {result.full_range_high_note}({result.full_range_high_midi}) "
        f"@{result.high_note_timestamp}s d={result.high_note_duration}s"
    )


def main() -> int:
    if len(sys.argv) not in (2, 3):
        print('Kullanım: python -m tools.song_ingestion.benchmark_separation "/yol.mp3" [etiket]', file=sys.stderr)
        return 1
    path = sys.argv[1]
    label = sys.argv[2] if len(sys.argv) == 3 else "x"
    if not Path(path).is_file():
        print(f"Dosya yok: {path}", file=sys.stderr)
        return 1

    # --- DIRECT ---
    mono, sr = decode_to_mono(path, DECODE_SR)
    duration = len(mono) / sr
    direct = analyze_audio(mono, sr)

    # --- SEPARATED ---
    h = content_hash(path)
    t_sep0 = time.perf_counter()
    stem_path = separate_vocals_stem(path, STEM_CACHE, h)
    sep_seconds = time.perf_counter() - t_sep0

    stem_mono, _ = decode_to_mono(stem_path, DECODE_SR)
    separated = analyze_audio(stem_mono, sr)

    # stem sağlık metrikleri
    stem_rms = float(np.sqrt(np.mean(stem_mono**2))) if len(stem_mono) else 0.0
    stem_peak = float(np.max(np.abs(stem_mono))) if len(stem_mono) else 0.0
    direct_valid = sum(s.duration for s in direct.segments)
    sep_valid = sum(s.duration for s in separated.segments)

    # Direct uçları separated stem'de hâlâ var mı? (±1 yarı ton toleransla segment ara)
    def present_in_separated(midi):
        if midi is None:
            return None
        return any(abs(s.midi - midi) <= 1 for s in separated.segments)

    low_present = present_in_separated(direct.full_range_low_midi)
    high_present = present_in_separated(direct.full_range_high_midi)

    # separated preview'lar (stem üzerinde)
    lo_prev = _write_preview(stem_mono, sr, separated.low_note_timestamp, f"separated_low_preview_{label}")
    hi_prev = _write_preview(stem_mono, sr, separated.high_note_timestamp, f"separated_high_preview_{label}")

    peak_ram = _peak_ram_mb()

    print("=" * 66)
    print(f"BENCHMARK — {Path(path).name}  (süre {duration:.1f} sn)")
    print(f"Ayrıştırma modeli: {SEPARATION_MODEL} (vocals stem — lead+backing içerebilir)")
    print("-" * 66)
    print("DIRECT RMVPE (orijinal miks):")
    print("  ", _fmt_extremes(direct))
    print(f"   tessitura {direct.tessitura_low_note}-{direct.tessitura_high_note} | "
          f"conf {direct.analysis_confidence} | voiced {direct.voiced_frame_ratio} | "
          f"avgRMVPE {direct.average_pitch_confidence} | segment {len(direct.segments)} | "
          f"geçerli vokal {round(direct_valid,1)}s | review {direct.review_status}")
    print()
    print("SEPARATED RMVPE (vocals stem):")
    print("  ", _fmt_extremes(separated))
    print(f"   tessitura {separated.tessitura_low_note}-{separated.tessitura_high_note} | "
          f"conf {separated.analysis_confidence} | voiced {separated.voiced_frame_ratio} | "
          f"avgRMVPE {separated.average_pitch_confidence} | segment {len(separated.segments)} | "
          f"geçerli vokal {round(sep_valid,1)}s | review {separated.review_status}")
    print()
    print("KİLİT SORU:")
    print(f"   Direct low  {direct.full_range_low_note}({direct.full_range_low_midi}) "
          f"→ separated stem'de {'HÂLÂ VAR' if low_present else 'KAYBOLDU'}")
    print(f"   Direct high {direct.full_range_high_note}({direct.full_range_high_midi}) "
          f"→ separated stem'de {'HÂLÂ VAR' if high_present else 'KAYBOLDU'}")
    print()
    print("STEM SAĞLIK KONTROLÜ:")
    print(f"   RMS {round(stem_rms,4)} | peak {round(stem_peak,3)} | "
          f"voiced Direct {direct.voiced_frame_ratio} → Separated {separated.voiced_frame_ratio} | "
          f"geçerli vokal {round(direct_valid,1)}s → {round(sep_valid,1)}s "
          f"(değişim {round(sep_valid-direct_valid,1)}s)")
    print()
    print("PERFORMANS:")
    print(f"   separation {round(sep_seconds,1)}s | separated RMVPE {separated.rmvpe_seconds}s | "
          f"direct RMVPE {direct.rmvpe_seconds}s | peak RAM ~{peak_ram} MB")
    print()
    print("PREVIEW (Git'e girmez):")
    print(f"   separated_low_preview_{label}:  {lo_prev}")
    print(f"   separated_high_preview_{label}: {hi_prev}")
    print("=" * 66)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
