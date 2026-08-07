"""Analiz motoru eşikleri — tek merkez.

Buradaki tüm değerler MVP HEURİSTİKLERİDİR; klinik/bilimsel bir standarda
dayanmaz. Gerçek şarkılarla calibration (Faz 2) yapıldıkça ayarlanacaktır.
Değerlerin gerekçeleri ve tessitura/confidence yöntemi docs/ANALYSIS_THRESHOLDS.md
içinde açıklanmıştır. Sihirli sayı kodun içine dağılmaz (bkz. CLAUDE.md).
"""

# RMVPE 16 kHz'de çalışır ve ~10 ms hop üretir.
RMVPE_SAMPLE_RATE = 16000
FRAME_HOP_SECONDS = 0.01

# ONNX Runtime çalıştırma sağlayıcısı. Apple Silicon'da CoreML EP, tam
# şarkı gibi UZUN/dinamik-şekilli girdilerde çöküyor ("Error in building plan")
# — araştırmanın öngördüğü CoreML dinamik-şekil kırılganlığı. CPU EP
# deterministik ve tek şarkı için yeterince hızlı; varsayılan bu. Hız gerekirse
# ve dinamik-şekil sorunları çözülürse ileride "coreml" denenebilir.
RMVPE_DEVICE = "cpu"

# ---------- 1) Frame filtreleme ----------
# RMVPE frame güveni bunun altındaysa frame güvenilmez sayılır ve atılır.
MIN_PITCH_CONFIDENCE = 0.5
# Geçerli F0 penceresi. Altı (bas enstrüman/gürültü) ve üstü (ıslık/overtone/
# takip hatası) insan şarkı vokali için fiziksel olarak anlamsız kabul edilir.
MIN_VALID_F0_HZ = 65.0    # ~C2
MAX_VALID_F0_HZ = 1100.0  # ~C#6

# ---------- 2) Nota segmentasyonu ----------
# Yuvarlamadan önce MIDI dizisine uygulanan hafif medyan yumuşatma penceresi
# (tek-frame yanlış sıçramaları/flip'leri azaltır). Tek (odd) olmalı.
MEDIAN_SMOOTH_FRAMES = 3
# Bir segment içindeki ardışık frame'ler arası izin verilen en büyük zaman
# boşluğu; bundan büyük boşluk segmenti keser (ayrı sesli bölüm başlar).
MAX_SEGMENT_GAP_SECONDS = 0.05
# Bir nota segmentinin GEÇERLİ sayılması için gereken en az süre ve frame sayısı.
# 20-30 ms'lik tek bir spike bu eşiği geçemez → full range'e giremez.
MIN_NOTE_DURATION_SECONDS = 0.06
MIN_SUPPORTING_FRAMES = 4
# Ardışık frame'ler arası bu kadar yarı tondan büyük fark, bir sonraki segmentin
# başlangıcı sayılır (aynı notaya birleşmez) ve "sıçrama" istatistiğine girer.
MAX_FRAME_JUMP_SEMITONES = 6.0

# ---------- 2b) Uç nota (boundary) — daha katı ----------
# Full range'in EN PES ve EN TİZ notası, tek/kısa bir segmentle belirlenmemeli;
# genel geçerlilikten daha uzun sürmeli. Böylece kısa bir yüksek geçiş/ad-lib
# full range'in ucu olarak kabul edilmez.
EXTREME_MIN_DURATION_SECONDS = 0.14
EXTREME_MIN_SUPPORTING_FRAMES = 10

# ---------- 3) Tessitura ----------
# Kabul edilen melodik vokal SÜRESİNİN bu oranını kaplayan en dar sürekli MIDI
# bandı tessitura kabul edilir (süre-ağırlıklı; tek kullanımlık ad-lib bandı
# genişletmez). Yöntem docs/ANALYSIS_THRESHOLDS.md'de açıklanmıştır.
TESSITURA_COVERAGE = 0.75

# ---------- 4) analysis_confidence formülü (ölçüm-tabanlı, sabit değil) ----------
# Ağırlıklı bileşenler (toplam 1.0). Skor bu bileşenlerden üretilir; ardından
# aşırı oktav-sıçrama oranı çarpımsal bir ceza uygular. Formül:
#   base = W_AVG*avg_conf + W_VOICED*voiced_ratio
#        + W_COVERAGE*coverage + W_EXTREME*extreme_support
#   confidence = base * (1 - JUMP_PENALTY * octave_jump_ratio)   → [0,1]'e sıkıştırılır
CONF_WEIGHT_AVG_CONFIDENCE = 0.40      # kabul edilen frame'lerin ortalama RMVPE güveni
CONF_WEIGHT_VOICED_RATIO = 0.20        # geçerli frame / toplam frame
CONF_WEIGHT_SEGMENT_COVERAGE = 0.20    # geçerli segment süresi / toplam süre
CONF_WEIGHT_EXTREME_SUPPORT = 0.20     # uç notaların ne kadar iyi desteklendiği
CONF_JUMP_PENALTY = 0.5                # oktav-sıçrama oranı bu katsayıyla düşürür

# ---------- 5) needs_review tetikleyicileri ----------
NEEDS_REVIEW_CONFIDENCE = 0.5          # analysis_confidence bunun altındaysa
MIN_VALID_FRAMES_FOR_RANGE = 30        # bundan az melodik frame varsa güvenilir range yok
SUSPICIOUS_RANGE_SEMITONES = 40        # bundan geniş range = şüpheli (çoklu ses/hata)
MAX_OCTAVE_JUMP_RATIO = 0.10           # ardışık geçerli frame'lerin bu oranından fazlası
                                       # büyük sıçrama içeriyorsa pitch track parçalı sayılır
