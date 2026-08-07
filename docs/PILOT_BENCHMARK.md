# Direct RMVPE — 5 Şarkılık Pilot Testi

Amaç: Direct RMVPE (vokal ayrıştırma YOK) pipeline'ının farklı Türkçe vokal
tiplerinde uç notaları ve tessitura'yı ne kadar güvenilir çıkardığını ölçmek.
**Bütün pilot boyunca mevcut eşikler değiştirilmez** (`tools/song_ingestion/config.py`),
aynı motor kullanılır. Vokal ayrıştırma (Pilot B) 5 şarkı bitmeden kurulmaz.

## Yöntem

- Her şarkı, kullanıcının kendi yerel dosyasıyla, olduğu yerden analiz edilir
  (kopyalanmaz, production'a hiçbir şey yazılmaz).
- Çalıştırma: `venv/bin/python -m tools.song_ingestion.analyze_file "<yol>" <etiket>`
- Her şarkı için low/high uç bölge preview'ları (±5 sn) üretilir; **kullanıcı
  bunları manuel olarak `doğru / yanlış / şüpheli` değerlendirir.**
- Sonuç production kataloğuna EKLENMEZ; pilot yalnızca doğruluk ölçümüdür.

## Vokal tipleri

| # | Tip | Şarkı | Durum |
| --- | --- | --- | --- |
| 1 | Kadın pop | Aleyna Tilki — Sen Olsan Bari | ✅ Tamamlandı (low ✅ / high ✅) |
| 2 | Erkek pop | Tarkan — Dudu | ✅ Tamamlandı (low ✅ / high ⚠️ needs review) |
| 3 | Arabesk / güçlü vibrato | Müslüm Gürses — Affet | ✅ Tamamlandı (low ✅ / high ❌ leakage; tessitura ✅) |
| 4 | Melodik rap / autotune | Poizi — Uyuyamadın Di Mi | ✅ Tamamlandı (low ⚠️ / high ✅; vocal_mode=melodic_rap) |
| 5 | Rock / yoğun enstrüman | Duman — Her Şeyi Yak | ✅ Tamamlandı (low ❌ bas gitar / high ✅) |

## Karar kuralı

- **5 şarkının en az 4'ünde uç notalar güvenilir** ise → Direct RMVPE ana
  pipeline olarak kalır.
- Sorunlu örnekler incelenip **yalnızca gerekirse** vokal separation fallback
  (Pipeline B) tasarlanır.
- 5 şarkı bitmeden Pipeline B kurulmaz.

---

## Sonuçlar

### 1. Kadın pop — Aleyna Tilki / Sen Olsan Bari · ✅ Başarılı

Analiz (CPU EP; CoreML uzun girdide çöktüğü için, bkz. K-068 güncellemesi):

| Alan | Değer |
| --- | --- |
| Süre | 189.1 sn |
| Metadata (title/artist) | yok (ID3 boş) — tahmin edilmedi |
| **Full range low** | **A#3** (MIDI 58) · 28.46 sn · destek 0.35 sn · median conf 0.819 |
| **Full range high** | **C5** (MIDI 72) · 40.74 sn · destek 0.16 sn · median conf 0.953 |
| **Tessitura** | **D4–G#4** (6 yarı ton) · geçerli vokalin %78'i |
| analysis_confidence | 0.652 |
| average RMVPE confidence | 0.789 |
| voiced_frame_ratio | 0.373 |
| discarded_frame_ratio | 0.627 |
| octave_jump_ratio | 0.0 |
| kabul edilen segment | 351 · toplam geçerli vokal 58.0 sn |
| needs_review | Hayır (pending) |
| İşlem süresi | model yükleme 1.28 sn · inference 3.56 sn · toplam 3.62 sn |

**Manuel doğrulama (kullanıcı):**
- Low (A#3): **DOĞRU**
- High (C5): **DOĞRU** — kısa bir geçiş/uç nota ama gerçek bir pitch olayı;
  full range içinde kalmalı, tessitura üzerinde belirleyici olmamalı (öyle:
  tessitura D4–G#4, C5 dışarıda).
- Tessitura (D4–G#4): kabul edilebilir.

**Direct RMVPE başarılı mı?** ✅ **Evet.**

### 2. Erkek pop — Tarkan / Dudu · ⚠️ Kısmi (low doğru, high şüpheli)

| Alan | Değer |
| --- | --- |
| Süre | 264.0 sn |
| Metadata | yok (ID3 boş) — tahmin edilmedi |
| **Full range low** | **F3** (MIDI 53) · 147.17 sn · destek 0.14 sn · median conf 0.796 |
| **Full range high** | **F#5** (MIDI 78) · 261.64 sn · destek 0.20 sn · median conf 0.55 |
| **Tessitura** | **F#3–F#4** (12 yarı ton) · geçerli vokalin %75'i |
| analysis_confidence | 0.63 |
| average RMVPE confidence | 0.742 |
| voiced_frame_ratio | 0.393 |
| discarded_frame_ratio | 0.607 |
| octave_jump_ratio | 0.001 |
| kabul edilen segment | 532 · toplam geçerli vokal 72.2 sn |
| needs_review | Hayır (pending) |
| İşlem süresi | model yükleme 1.53 sn · inference 4.74 sn · toplam 4.85 sn |

**Manuel doğrulama (kullanıcı):**
- `low_manual_verification = approved` — F3 (147.17 sn) gerçek ve yeterince güvenilir.
- `high_manual_verification = needs_review` — F#5 tamamen rastgele hata değil
  (bölgede ~710–743 Hz'lik gerçek bir perdeli olay var), ama **ana vokal olduğu
  güvenilir şekilde doğrulanamıyor**: outro'da olması, median conf 0.55, yalnızca
  0.20 sn destek, efekt/backing vocal/melodik enstrüman olasılığı. Yanlış olarak
  işaretlenmedi; `human_verified high` olarak da kabul edilmedi.

**Not edilen sınırlama:** *Direct RMVPE'nin kısa, düşük-confidence tiz/outro
olaylarında kaynak atfı (bu ana vokal mi, backing/efekt/enstrüman mı?) yapamaması.*
Bu, ileride ayrıştırma fallback'inin (Pipeline B) değerlendirileceği ilk somut
gerekçe adayı — ama karar 5 şarkı bitmeden verilmeyecek, eşikler/pipeline
değiştirilmeyecek.

**Direct RMVPE başarılı mı?** ⚠️ **Kısmi** — low güvenilir, high doğrulanamadı.

### 3. Arabesk / güçlü vibrato — Müslüm Gürses / Affet · ⚠️ Kısmi (tessitura doğru, high leakage)

| Alan | Değer |
| --- | --- |
| Süre | 275.6 sn |
| Metadata | yok (ID3 boş) — tahmin edilmedi |
| **Full range low** | **A2** (MIDI 45) · 173.87 sn · destek 0.26 sn · median conf 0.697 |
| **Full range high** | **A#5** (MIDI 82) · 231.64 sn · destek 0.43 sn · median conf 0.649 |
| **Tessitura** | **G3–D4** (7 yarı ton) · geçerli vokalin %82'si |
| analysis_confidence | 0.633 |
| average RMVPE confidence | 0.769 |
| voiced_frame_ratio | 0.357 |
| discarded_frame_ratio | 0.643 |
| octave_jump_ratio | 0.0003 |
| kabul edilen segment | 522 · toplam geçerli vokal 74.2 sn |
| needs_review | Hayır (pending) |
| İşlem süresi | model yükleme 1.28 sn · inference 4.94 sn · toplam 5.04 sn |

**Manuel doğrulama (kullanıcı):**
- `low_manual_verification = approved` — A2 (~110 Hz temel + 220/330/440 Hz
  uyumlu harmonik yapı). Gerçek vokal olarak kabul edilebilir.
- `high_manual_verification = rejected_non_lead_vocal` — RMVPE yanlış pitch
  UYDURMADI: ~920–930 Hz'de gerçekten güçlü, A#5 ile uyumlu bir perdeli kaynak
  var. Ama spektral incelemede bu bölgenin ana vokal olduğuna dair yeterli
  harmonik yapı yok (enerji ~925 Hz'deki tek bileşende yoğun, üst harmonikler
  ana vokal için beklenenden zayıf). Kaynak muhtemelen enstrüman/efekt/backing
  vocal. **Full range'i yanlış genişleten bir leakage.**

**Not edilen bulgu:** *Direct RMVPE, pitch tespitinde doğru olabilse de full
mix üzerinde pitch kaynağının ana vokal olup olmadığını ayıramıyor. Özellikle
tiz uçlarda enstrüman/backing vocal leakage full range'i yanlış genişletebiliyor.*
(2. şarkıdaki desenin daha kesin biçimi — bu kez "şüpheli" değil, "ana vokal
değil" olarak reddedildi.)

**Tessitura G3–D4:** ✅ makul/başarılı — güçlü vibratoya rağmen segmentasyon
çökmedi (octave_jump 0.0003), pes erkek arabesk merkezi doğru, vokalin %82'si.

**Direct RMVPE başarılı mı?** ⚠️ **Kısmi** — tessitura doğru, low doğru, high
yanlış (leakage full range'i şişirdi).

### 4. Melodik rap / autotune — Poizi / Uyuyamadın Di Mi · ⚠️ Kısmi (melodic_rap — anlam sınırlı)

| Alan | Değer |
| --- | --- |
| Süre | 158.8 sn |
| Metadata | **VAR** — başlık "POIZI - UYUYAMADIN Dİ Mİ (Official Video)", sanatçı "Poizi" (ID3'ten) |
| **Full range low** | **F#3** (MIDI 54) · 90.57 sn · destek 0.21 sn · median conf 0.801 |
| **Full range high** | **E4** (MIDI 64) · 66.6 sn · destek 0.22 sn · median conf 0.804 |
| **Tessitura** | **A#3–D4** (4 yarı ton) · geçerli vokalin %75'i |
| analysis_confidence | 0.79 (pilotta en yüksek) |
| average RMVPE confidence | 0.803 |
| voiced_frame_ratio | 0.711 (öncekiler ~0.37; iki kat) |
| discarded_frame_ratio | 0.289 |
| octave_jump_ratio | 0.0 |
| kabul edilen segment | 492 · toplam geçerli vokal 100.7 sn |
| needs_review | Hayır (pending) |
| İşlem süresi | model yükleme 1.2 sn · inference 2.96 sn · toplam 3.06 sn |

**Manuel doğrulama (kullanıcı):**
- `low_manual_verification = needs_review` — F#3 (~185 Hz) harmonik desteği var
  (~370/740/925 Hz), ama aynı bölgede F3 (~174.6 Hz) civarında da güçlü bir
  perdeli yapı var; iki kaynak üst üste biniyor veya kısa bir pitch geçişi
  olabilir. Rejected değil, approved da değil.
- `high_manual_verification = approved` — E4 (~329–330 Hz + 660/1320 Hz uyumlu
  harmonikler) açık şekilde gerçek.
- `vocal_mode = melodic_rap` (manuel etiket).

**⚠️ Önemli kural (kullanıcı):** *Yüksek voiced_frame_ratio veya yüksek RMVPE
confidence tek başına autotune/melodic_rap sınıflandırma kuralı olarak
KULLANILMAYACAK — bu ilişki henüz doğrulanmadı.* (Bu şarkıda ikisi de yüksek
çıktı ama bu bir gözlem, kanıt değil.)

**Tessitura A#3–D4:** ✅ başarılı/makul — dar, konuşma-benzeri bir bant;
melodik rap için beklenen. Ama "vokal aralığı"nın anlamı gerçek şarkıcıdan farklı.

**Direct RMVPE başarılı mı?** ⚠️ **Kısmi** — high doğru, low needs_review,
tessitura makul; ama parça melodic_rap olduğu için aralığın anlamı sınırlı.

### 5. Rock / yoğun enstrüman — Duman / Her Şeyi Yak · ⚠️ Kısmi (low bas gitar leakage)

| Alan | Değer |
| --- | --- |
| Süre | 243.0 sn |
| Metadata | **VAR** — başlık "Duman - Her Şeyi Yak", sanatçı "Duman" (ID3'ten) |
| **Full range low** | **D2** (MIDI 38) · 143.01 sn · destek 0.17 sn · median conf 0.516 |
| **Full range high** | **G4** (MIDI 67) · 50.35 sn · destek 0.20 sn · median conf 0.631 |
| **Tessitura** | **C3–D4** (14 yarı ton) · geçerli vokalin %76'sı |
| analysis_confidence | 0.612 |
| average RMVPE confidence | 0.732 |
| voiced_frame_ratio | 0.343 |
| discarded_frame_ratio | 0.657 |
| octave_jump_ratio | 0.012 (5 şarkının en yükseği) |
| kabul edilen segment | 364 · toplam geçerli vokal 65.8 sn |
| needs_review | Hayır (pending) |
| İşlem süresi | model yükleme 1.30 sn · inference 4.40 sn · toplam 4.48 sn |

**Manuel doğrulama (kullanıcı):**
- `low_manual_verification = rejected_non_lead_vocal` — ~73–74 Hz temel +
  148/221/293 Hz düzenli azalan harmonik: güçlü gerçek pitch, ama rock miksinde
  **bas gitar** (ana vokal değil). median conf 0.516 (eşiğin hemen üstü), D2
  bas gitar bölgesiyle örtüşüyor.
- `high_manual_verification = approved` — ~392–401 Hz (G4) + 784/1176/1568 Hz
  uyumlu harmonik devam. Ana vokal için makul.

**Tessitura C3–D4:** ✅ makul/başarılı.

**Direct RMVPE başarılı mı?** ⚠️ **Kısmi** — high doğru, tessitura doğru, low
yanlış (bas gitar leakage full range'i aşağı şişirdi).

---

## Pilot Sonucu (5/5 tamamlandı)

### Toplu tablo — nihai manuel doğrulamalar

| # | Şarkı | Low | Low doğrulama | High | High doğrulama | Tessitura | Conf | Sonuç |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Aleyna Tilki — Sen Olsan Bari | A#3 | ✅ approved | C5 | ✅ approved | D4–G#4 ✅ | 0.652 | ✅ Her iki uç temiz |
| 2 | Tarkan — Dudu | F3 | ✅ approved | F#5 | ⚠️ needs_review | F#3–F#4 ✅ | 0.63 | ⚠️ Kısmi |
| 3 | Müslüm Gürses — Affet | A2 | ✅ approved | A#5 | ❌ rejected (non-lead) | G3–D4 ✅ | 0.633 | ⚠️ Kısmi |
| 4 | Poizi — Uyuyamadın Di Mi *(melodic_rap)* | F#3 | ⚠️ needs_review | E4 | ✅ approved | A#3–D4 ✅ | 0.79 | ⚠️ Kısmi |
| 5 | Duman — Her Şeyi Yak | D2 | ❌ rejected (non-lead) | G4 | ✅ approved | C3–D4 ✅ | 0.612 | ⚠️ Kısmi |

### Karar kuralının sonucu

Kural: *5 şarkının en az 4'ünde uç notalar güvenilir ise Direct RMVPE tek başına
ana pipeline kalır.*

- **Her iki uç da temiz (approved): yalnızca 1/5** (Aleyna Tilki). Eşik (4/5)
  **karşılanmadı.**
- **Tessitura: 5/5 makul/başarılı** — melodik rap ve güçlü vibrato dahil.
- Uçlar tek tek: low 3 approved / 1 needs_review / 1 rejected; high 3 approved /
  1 needs_review / 1 rejected. Her uç bağımsız olarak ~%60 güvenilir.

### Teknik karar (kullanıcı onaylı yön)

**Direct RMVPE:**
- Tessitura tahmininde 5/5 makul → öneri için asıl kullandığımız çıktı sağlam.
- Full-range uçlarında güvenilir değil.
- **Asıl hata pitch detection değil, source attribution:** full mix içindeki bas
  gitar / yaylı / backing vocal / efekt / başka melodik kaynak ana vokal
  sanılabiliyor.
- Sadece duration/confidence eşiğini artırmak bunu tam çözmez; bazı yanlış
  kaynaklar (Müslüm A#5, Duman D2) uzun süreli, gerçek ve yüksek güvenli pitch
  üretiyor.

**Önerilen mimari — adaptif iki aşama:**
- **Stage A (her şarkı):** Direct RMVPE → nota segmentasyonu → tessitura →
  aday full-range uçları → güven/risk değerlendirmesi.
- **Stage B (yalnızca gerektiğinde):** şüpheli uç veya düşük source-confidence
  varsa → vocal separation → separated lead-vocal RMVPE → aday uç doğrulama.

Amaç her şarkıya separation çalıştırmak DEĞİL. Şüphe tetikleyicileri (aday):
düşük RMVPE confidence, çok kısa uç, sıra dışı geniş full range, uç'un
tessitura'dan aşırı uzak olması, intro/outro'da olması, rock/arabesk gibi
yüksek leakage riskli miks, Direct ve separated sonuçlarının uyuşmaması.

**Bu pilot sonrası:** eşikler DEĞİŞMEDİ, pilot şarkıları production kataloğuna
EKLENMEDİ, production'a ağır bağımlılık EKLENMEDİ. Pipeline B için önce yalnızca
teknik plan hazırlanacak (bkz. docs/DECISIONS.md K-070); model kurulmayacak.

*(Nihai toplu tablo yukarıda "Pilot Sonucu" bölümündedir.)*
