# Sestiny — Proje Planı

## 1. Ürünün amacı

Sestiny, kullanıcıdan üç farklı ses kaydı alarak yaklaşık bir ses profili çıkaran ve
kullanıcının ses aralığına uygun şarkılar önermeyi hedefleyen bir web uygulamasıdır.

Ürün **tıbbi veya profesyonel bir teşhis aracı değildir**. Tüm çıktılar "tahmini",
"gözlemlenen", "yaklaşık" dilinde sunulur.

## 2. Kullanıcı akışı (ilk sürüm)

1. Karşılama ekranı ve kısa açıklama
2. Sonuçların kesin teşhis olmadığına dair bilgilendirme
3. Mikrofon izni
4. Sessiz ortam / mikrofon mesafesi kontrolü + kısa mikrofon denemesi
5. **Test 1 — Konuşma testi**
6. **Test 2 — Uzun "A" sesi**
7. **Test 3 — Kalından inceye kaydırma (glide)**
8. Kayıtları dinleme, gerekirse yeniden kaydetme
9. Analiz süreci (gerçek aşama mesajlarıyla)
10. Tahmini ses profili sonucu
11. Şarkı önerileri
12. Testi yeniden yapma

İlk sürümde hesap, ödeme ve geçmiş testler yoktur.

## 3. Ses testleri özeti

| # | Test | Min | Önerilen | Maks | Ana çıktılar |
| --- | --- | --- | --- | --- | --- |
| 1 | Konuşma | 3 sn | 5–10 sn | 15 sn | Medyan F0, yaklaşık nota, perde değişkenliği, voiced oranı |
| 2 | Uzun "A" | 2 sn | 5–12 sn | 20 sn | Medyan F0, nota, sesli süre, cents sapma, stabilite skoru |
| 3 | Glide | 3 sn | 6–12 sn | 20 sn | Gözlemlenen alt/üst nota, aralık genişliği, tahmini rahat bölge |

**Test 1 cümlesi:** "Merhaba, bugün sesimi analiz etmek için kısa bir kayıt yapıyorum."

Ortalama konuşma perdesi için **aritmetik ortalama değil medyan F0** kullanılır
(aykırı değerlerden daha az etkilenir).

## 4. Mimari

```
Tarayıcı (React + TS + Vite)
   │  MediaRecorder ile 3 ayrı ses kaydı (Blob)
   │  multipart/form-data: speech, sustained_vowel, glide
   ▼
FastAPI backend (lokal, 127.0.0.1:8000)
   │  1. Dosya doğrulama (format, boyut, magic bytes)
   │  2. Geçici güvenli dosyaya yaz
   │  3. Format dönüştürme → mono, sabit örnekleme oranı
   │  4. Kayıt kalitesi kontrolü (süre, RMS, clipping, sessizlik)
   │  5. Pitch analizi (librosa.pyin) → F0 → MIDI → nota
   │  6. Profil oluşturma + güven skoru
   │  7. Şarkı eşleştirme (yerel JSON verisi)
   │  8. Geçici dosyaları sil
   ▼
JSON cevap → sonuç ekranı + öneri kartları
```

Veritabanı yoktur; şarkı verisi backend içinde JSON dosyasında tutulur.
Ham ses hiçbir aşamada kalıcı saklanmaz.

## 5. Klasör yapısı (hedef)

```
Sestiny/                     ← proje kökü (bu klasör)
├── frontend/
│   ├── src/
│   │   ├── api/             backend çağrıları
│   │   ├── components/      paylaşılan UI parçaları
│   │   ├── features/
│   │   │   ├── onboarding/
│   │   │   ├── microphone-check/
│   │   │   ├── voice-tests/
│   │   │   ├── analysis/
│   │   │   └── recommendations/
│   │   ├── hooks/           useRecorder vb.
│   │   ├── types/           API tipleri
│   │   ├── utils/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/             health.py, analysis.py
│   │   ├── core/            config.py (tüm eşikler), logging.py
│   │   ├── schemas/         analysis.py (Pydantic)
│   │   ├── services/        audio_conversion, audio_quality,
│   │   │                    pitch_analysis, profile_builder, recommendation
│   │   └── data/            demo_songs.json
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── docs/
├── CLAUDE.md
├── README.md
├── .gitignore
└── .env.example
```

Klasörler **kullanıldıkları aşamada** oluşturulur; boş iskelet klasör bırakılmaz.

## 6. Analiz yaklaşımı

- Pitch takibi: `librosa.pyin`, arama aralığı ~C2 (65.4 Hz) – C7 (2093 Hz),
  kod içinde açıklamalı sabit olarak tanımlanır.
- Düşük `voiced_prob` değerli frame'ler elenir; fiziksel olarak anlamsız ani
  sıçramalar ve oktav hataları filtrelenir; medyan yumuşatma uygulanır.
- Hz → MIDI: `69 + 12 * log2(f / 440)`. A4 = 440 Hz. Nota adları diyezli gösterilir (C#3, F#4).
- **Tahmini rahat bölge:** uç değerler doğrudan kullanılmaz; güvenilir F0 dağılımının
  ~%5 ve ~%95 noktaları gözlemlenen uçlar kabul edilir, rahat bölge bundan daha dar tutulur.
  Güven düşükse rahat bölge "güvenilir şekilde belirlenemedi" olarak gösterilir.
- **Stabilite skoru (0–100):** cents cinsinden medyan mutlak sapma, dropout oranı,
  ani sıçrama sayısı, voiced oranı ve süre yeterliliğinden oluşan bir heuristiktir.
  Eşikler (80+ stabil, 55–79 orta, <55 geliştirilebilir) **klinik standart değildir**;
  bu, kodda ve belgelerde açıkça yazılır.

## 7. Şarkı öneri sistemi

Veri modeli: `id, title, artist, language, genre, min_midi, max_midi, min_note,
max_note, difficulty, verified, source_note, optional_transposition_limit`

Algoritma: kullanıcının tahmini rahat aralığı ile şarkı aralığının örtüşmesinden
0–100 eşleşme skoru; 1–3 semiton taşma varsa ton değiştirme önerisi; zorluk skora
dahil edilir; en uygun 5–10 sonuç sıralanır.

**İlk sürümde gerçek şarkı aralıkları uydurulmaz.** Yalnızca açıkça kurgu
("Demo Şarkı 1") örnekler kullanılır; gerçek liste sonradan doğrulanmış veriyle eklenir.

## 8. Geliştirme aşamaları

Her aşama sonunda **durulur ve kullanıcının "devam" onayı beklenir**.

| Aşama | İçerik | Durum |
| --- | --- | --- |
| 0 | Ortam kontrolü, planlama, belgeler, Git | ✅ Tamamlandı |
| 1 | Vite+React ve FastAPI iskeleti, `/api/v1/health`, CORS, bağlantı doğrulama | ✅ Tamamlandı |
| 2 | Mikrofon izni, üç test ekranı, kayıt/dinleme/silme akışı | ✅ Tamamlandı |
| 3 | `POST /api/v1/analyze-session`, dosya doğrulama, geçici dosya yönetimi, kalite kontrolü | ✅ Tamamlandı |
| 4 | librosa pitch analizi, profil oluşturma, sentetik ses testleri | ✅ Tamamlandı |
| 5 | Sonuç ekranı (Türkçe kartlar, uyarı metni, düşük güven durumları) | ✅ Tamamlandı |
| 6 | Demo şarkı verisi, eşleştirme algoritması, öneri kartları | ✅ Tamamlandı |
| 7 | Testler, erişilebilirlik, mobil kontrol, kod temizliği, dokümantasyon | ✅ Tamamlandı |
| 8 | Yayına hazırlık — **yalnızca ayrıca açık onay verilirse** | 🚧 Kod hazır; canlı deploy kullanıcı eylemi bekliyor (bkz. K-051) |

### Aşama kabul kriterleri

- **1:** Backend ve frontend başlıyor, health 200 dönüyor, ekranda başarı mesajı var, konsolda kritik hata yok.
- **2:** Üç kayıt ayrı ayrı yapılabiliyor, dinlenebiliyor, yeniden kaydedilebiliyor; izin reddi doğru yönetiliyor.
- **3:** Üç kayıt backend'e ulaşıyor, geçerli kabul / geçersiz reddediliyor, geçici dosyalar temizleniyor.
- **4:** A3 (220 Hz) ve C4 (261.63 Hz) sentetik testleri tolerans içinde doğru; sessiz seste nota uydurulmuyor.
- **5:** JSON kullanıcı dostu Türkçe kartlara dönüşüyor, düşük güven açıkça anlatılıyor, mobilde düzgün.
- **6:** Demo veriden tutarlı öneri çıkıyor, aralık değişince sıralama değişiyor, ton önerisi matematiksel doğru.
- **7:** Tüm testler geçiyor, README doğrulanmış kurulum adımları içeriyor.
- **8:** Prod-güvenli varsayılanlar (debug kapalı), CORS gerçek frontend origin'ine
  ayarlanabilir, hız sınırlama çalışıyor ve test ediliyor, deploy manifestleri
  (render.yaml, runtime.txt) mevcut, README'de numaralı Render+Vercel kontrol
  listesi var. **Gerçek canlı URL'lerin çalıştığının doğrulanması bu kabul
  kriterinin dışında** — hesap açma/deploy kullanıcı eylemi gerektirir, yapay
  zekâ asistanı tarafından doğrulanamaz (bkz. `docs/PROGRESS.md`).

## 9. Test planı

**Backend (pytest, sentetik sesler kodla üretilir — depoya ses dosyası konmaz):**
health endpoint, geçersiz format, çok büyük dosya, çok kısa ses, sessiz ses,
220 Hz→A3, 261.63 Hz→C4, stabil sinüs stabilite, dalgalanan sinüs stabilite,
sentetik glide alt/üst nota, geçici dosya silinmesi, response şeması.

**Frontend (Vitest + Testing Library):** karşılama ekranı açılıyor, mikrofon izni
reddinde hata mesajı, kayıt durumu değişimi, eksik testte analiz butonu pasif,
backend hatasında anlaşılır mesaj, sonuç verisi doğru kartlara yerleşiyor.

## 10. Bilinen sınırlamalar

- Tek bir glide kaydı gerçek tessiturayı kesin belirleyemez.
- Tarayıcı mikrofonları otomatik kazanç/gürültü bastırma uygular; mutlak ses seviyesi güvenilir değildir.
- pyin oktav hatası yapabilir; filtreleme bunu azaltır ama tamamen ortadan kaldırmaz.
- Şarkı önerileri, doğrulanmış gerçek şarkı verisi eklenene kadar yalnızca demo niteliğindedir.
