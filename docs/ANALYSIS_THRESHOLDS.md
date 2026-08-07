# Analiz Eşikleri ve Yöntemleri (Song Ingestion Lab)

Bu belge, `tools/song_ingestion/` içindeki **Direct RMVPE** analiz motorunun
eşiklerini ve yöntemlerini açıklar. **Tüm değerler MVP heuristiğidir** — klinik
veya bilimsel bir standarda dayanmaz. Gerçek şarkılarla calibration (Faz 2)
yapıldıkça ayarlanacaktır. Kaynak: `tools/song_ingestion/config.py`.

## Boru hattı (Pipeline A — Direct)

```
ses → RMVPE (F0 + frame güveni) → frame filtreleme → nota segmentasyonu
    → full range (uç-nota eşiğiyle) + tessitura (süre-ağırlıklı)
    → analysis_confidence → needs_review kararı
```

Vokal ayrıştırma YOK — RMVPE tam mikse doğrudan uygulanır. Ayrıştırmanın
doğruluğu artırıp artırmadığı Faz sonrası ayrı benchmark edilecektir (Pipeline B);
ölçmeden zorunlu kılınmaz.

## 1. Frame filtreleme

| Eşik | Değer | Neden |
| --- | --- | --- |
| `MIN_PITCH_CONFIDENCE` | 0.5 | RMVPE frame güveni bunun altındaysa frame güvenilmez, atılır |
| `MIN_VALID_F0_HZ` | 65.0 (~C2) | Altı bas enstrüman/gürültü |
| `MAX_VALID_F0_HZ` | 1100.0 (~C#6) | Üstü ıslık/overtone/takip hatası |

## 2. Nota segmentasyonu

Ham min/max **asla** doğrudan kullanılmaz. Frame-level MIDI dizisine hafif
medyan yumuşatma uygulanır, en yakın yarım tona yuvarlanır, ardışık aynı-notalı
(ve zamanda yakın) frame'ler bir segmentte birleşir.

| Eşik | Değer | Neden |
| --- | --- | --- |
| `MEDIAN_SMOOTH_FRAMES` | 3 | Tek-frame yanlış sıçramaları/flip'leri azaltır |
| `MAX_SEGMENT_GAP_SECONDS` | 0.05 | Bundan büyük boşluk segmenti keser |
| `MIN_NOTE_DURATION_SECONDS` | 0.06 | Bir segmentin geçerli sayılması için (20-30 ms spike elenir) |
| `MIN_SUPPORTING_FRAMES` | 4 | Segment en az bu kadar frame içermeli |
| `MAX_FRAME_JUMP_SEMITONES` | 6.0 | Ardışık frame'ler arası bundan büyük fark = yeni segment + "sıçrama" istatistiği |

**Glide davranışı:** Yuvarlayarak segmentleme sayesinde bir glide her yarım
tondan kısa süre geçer → her yarım ton kısa bir segment olur; binlerce parçaya
bölünmez. Saf glide'da uç notalara yalnızca yarım yarım-ton süresi kadar
dokunulduğu için, uç-nota eşiği (aşağıda) uçtan bir yarım ton kırpabilir — bu
istenen davranıştır (anlık dokunulan uç şişirilmez).

## 2b. Uç nota (full range boundary) — daha katı

Full range'in en pes ve en tiz notası, genel geçerlilikten **daha uzun**
desteklenmiş segmentlerden seçilir:

| Eşik | Değer | Neden |
| --- | --- | --- |
| `EXTREME_MIN_DURATION_SECONDS` | 0.14 | Uç nota bu kadar sürmeli; kısa bir tiz geçiş/ad-lib ucu belirlemez |
| `EXTREME_MIN_SUPPORTING_FRAMES` | 10 | Uç nota bu kadar frame'le desteklenmeli |

Uç-nota eşiğini geçen segment yoksa **aralık üretilmez** (needs_review).

## 3. Tessitura (yöntem)

Tessitura, full range'den **ayrı** hesaplanır. Amaç: melodik vokalin büyük
bölümünde kalınan merkez bölge.

**Yöntem:** Kabul edilen her segmentin süresi, MIDI notasına göre bir
histograma eklenir (süre-ağırlıklı). Ardından en pesten en tize sürekli
pencereler taranır ve toplam vokal süresinin `TESSITURA_COVERAGE` oranını
karşılayan **en dar** pencere seçilir.

| Parametre | Değer | Neden |
| --- | --- | --- |
| `TESSITURA_COVERAGE` | 0.75 | Vokal süresinin ~%75'ini kaplayan en dar bant |

Tek kullanımlık bir ad-lib (kısa toplam süre) bu bandı genişletmez — kapsama
hedefine ulaşmak için ona ihtiyaç kalmaz, pencere merkez kütlede dar kalır.
%75 seçimi heuristiktir; calibration'da ayarlanabilir.

## 4. analysis_confidence (formül)

Keyfi sabit **değildir**; ölçülen bileşenlerden üretilir:

```
base = 0.40·avg_conf + 0.20·voiced_ratio + 0.20·coverage + 0.20·extreme_support
confidence = base · (1 − 0.5·octave_jump_ratio)      →  [0,1]
```

| Bileşen | Anlamı |
| --- | --- |
| `avg_conf` | Kabul edilen frame'lerin ortalama RMVPE güveni |
| `voiced_ratio` | Geçerli frame / toplam frame |
| `coverage` | Geçerli segment süresi / toplam ses süresi |
| `extreme_support` | Uç notaların daha zayıfının süresi / `EXTREME_MIN_DURATION` (≤1) |
| `octave_jump_ratio` | Ardışık geçerli frame'ler arası büyük sıçrama oranı (çarpımsal ceza) |

Ağırlıklar `config.py`'de (`CONF_WEIGHT_*`, `CONF_JUMP_PENALTY`). Heuristiktir.

## 5. needs_review tetikleyicileri

Aşağıdakilerden herhangi biri `review_status = needs_review` üretir; sebepler
`needs_review_reason` listesinde döner:

| Koşul | Eşik |
| --- | --- |
| Düşük analiz güveni | `analysis_confidence < NEEDS_REVIEW_CONFIDENCE` (0.5) |
| Çok az melodik frame | `valid_frames < MIN_VALID_FRAMES_FOR_RANGE` (30) |
| Güvenilir uç nota/tessitura yok | uç-nota eşiğini geçen segment yok |
| Sıra dışı geniş aralık | `range_semitones > SUSPICIOUS_RANGE_SEMITONES` (40) |
| Parçalı pitch track | `octave_jump_ratio > MAX_OCTAVE_JUMP_RATIO` (0.10) |

Bu eşiklerin hepsi başlangıç değerleridir ve gerçek şarkı calibration'ında
(Faz 2) gözden geçirilecektir.
