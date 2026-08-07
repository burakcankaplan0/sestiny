"""Robust aralık + tessitura hesabı — ham min/max ASLA doğrudan kullanılmaz.

Adımlar (bkz. plan Q3-bis):
1. Yalnızca güvenli (frame confidence ≥ eşik) ve sürekli (aynı yarım tonda
   ≥ min süre tutulan, kümelenmiş) frame'ler alınır. 30 ms'lik tek bir F6 nota
   sayılmaz.
2. Full range: ham uç yerine robust yüzdelik (alt ~2-5, üst ~95-98) — tek-frame
   oktav hatası/glitch elenir. Bir sınır notasının kabulü için ≥ N tutarlı
   tahmin şartı. En pes ve en tiz notanın zamanı (timestamp) kaydedilir.
3. Tessitura: her nota toplam söylenen süreyle ağırlıklanır, pitch histogramı
   kurulur, söylenen zamanın ~%70'ini kaplayan merkez bant alınır.

Not: backend/app/services/pitch_analysis.py'deki iki yaklaşım burada yeniden
kullanılacaktır: `_remove_pitch_jumps` (oktav-hatası eleme) ve yüzdelik-tabanlı
rahat-bölge (tessitura'nın temeli zaten bu).

BU MODÜL FAZ 1'DE DOLDURULACAK — parametreler burada, mantık Faz 1'de.
"""

from __future__ import annotations

from dataclasses import dataclass

FRAME_CONFIDENCE_THRESHOLD = 0.72  # bu güvenin altındaki frame'ler atılır
MIN_CONSISTENT_ESTIMATES_FOR_BOUNDARY = 10  # bir uç notayı kabul için
FULL_RANGE_LOW_PERCENTILE = 3
FULL_RANGE_HIGH_PERCENTILE = 97
TESSITURA_COVERAGE = 0.70  # söylenen zamanın bu oranını kaplayan merkez bant


@dataclass(frozen=True)
class RangeResult:
    full_range_low_midi: int
    full_range_high_midi: int
    tessitura_low_midi: int
    tessitura_high_midi: int
    detected_low_timestamp: float
    detected_high_timestamp: float


def compute_range(pitch_frames) -> "RangeResult | None":
    """Güvenli/sürekli frame'lerden full range + tessitura + timestamp'ler.

    Yeterli güvenilir melodik veri yoksa None döner (aralık uydurulmaz).
    Faz 1'de doldurulacak.
    """
    raise NotImplementedError("Robust aralık + tessitura Faz 1'de eklenecek.")
