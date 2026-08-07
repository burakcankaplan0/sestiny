"""analysis_confidence hesabı — ÖLÇÜLEN kaliteden türetilir, sabit sayı DEĞİL.

Kullanıcının katı isteği (plan 8. madde): "MIDI = 0.9", "Audio = 0.7" gibi keyfi
eşleme YOK. Güven, gerçekten ölçülen sinyal kalitesinden gelir. `source_type`
ayrı bir alandır (audio_analysis + confidence 0.93 + human_verified true mümkün).

Girdiler (hepsi 0-1 civarı, ölçülen):
- qualified_frame_ratio: nitelikli (güvenli + sürekli) frame / toplam voiced frame
- boundary_support: uç notaları destekleyen tutarlı tahmin sayısının yeterliliği
- separation_bleed: ayrıştırma sonrası kalıntı vokal-dışı enerji (yüksek = kötü)
- sustained_note_ratio: sung oranı (rap'e yakınsa güven düşer)

BU MODÜL FAZ 1'DE DOLDURULACAK — girdi sözleşmesi burada.
"""

from __future__ import annotations


def compute_confidence(
    *,
    qualified_frame_ratio: float,
    boundary_support: float,
    separation_bleed: float,
    sustained_note_ratio: float,
) -> float:
    """Ölçülen kalite bileşenlerinden 0-1 güven üretir. Faz 1'de doldurulacak."""
    raise NotImplementedError("Ölçüm-tabanlı güven Faz 1'de eklenecek.")
