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
| 1 | Kadın pop | Aleyna Tilki — Sen Olsan Bari | ✅ Tamamlandı |
| 2 | Erkek pop | (bekleniyor) | ⬜ |
| 3 | Arabesk / güçlü vibrato | (bekleniyor) | ⬜ |
| 4 | Melodik rap / autotune | (bekleniyor) | ⬜ |
| 5 | Rock / yoğun enstrüman | (bekleniyor) | ⬜ |

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

### 2-5

(bekleniyor)

---

## Toplu tablo (5 şarkı bitince doldurulacak)

| Şarkı | Low sonucu | Low doğrulama | High sonucu | High doğrulama | Tessitura | Confidence | Direct RMVPE başarılı? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1. Aleyna Tilki — Sen Olsan Bari | A#3 | ✅ Doğru | C5 | ✅ Doğru | D4–G#4 | 0.652 | ✅ Evet |
| 2. | | | | | | | |
| 3. | | | | | | | |
| 4. | | | | | | | |
| 5. | | | | | | | |
