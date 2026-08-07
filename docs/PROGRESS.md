# İlerleme Kaydı

---

## Aşama 0 — Ortam ve Plan · 2026-08-04 · ✅ Tamamlandı

### Yapılanlar

- Çalışma klasörü incelendi: `~/Desktop/Sestiny` tamamen boştu.
- Kurulu araçların sürümleri tespit edildi (aşağıdaki tablo).
- Proje kökü olarak mevcut klasör seçildi (bkz. DECISIONS K-001).
- Git deposu başlatıldı ve ilk commit yapıldı.

### Oluşturulan dosyalar

| Dosya | İçerik |
| --- | --- |
| `CLAUDE.md` | Projenin bağlayıcı geliştirme ve ürün kuralları |
| `README.md` | Proje tanıtımı, teknoloji tablosu, gereksinimler, gizlilik notu |
| `.gitignore` | `.env`, `node_modules`, `.venv`, **tüm ses formatları**, geçici klasörler |
| `.env.example` | Gizli bilgi içermeyen örnek ortam değişkenleri |
| `docs/PROJECT_PLAN.md` | Mimari, kullanıcı akışı, analiz yaklaşımı, aşamalar, test planı |
| `docs/DECISIONS.md` | 11 teknik karar (K-001 … K-011) gerekçeleriyle |
| `docs/PROGRESS.md` | Bu dosya |

### Tespit edilen ortam

| Araç | Durum |
| --- | --- |
| Git | ✅ 2.50.1 |
| Homebrew | ✅ 5.0.7 (`/opt/homebrew`) |
| Python | ⚠️ 3.9.6 (Xcode ile gelen sistem Python'u) — 3.11+ gerekli |
| Node.js / npm | ❌ kurulu değil |
| FFmpeg | ❌ kurulu değil |

### Kurulmadı / yapılmadı

- **Hiçbir paket kurulmadı.** Node.js ve Python 3.12 kurulumu sistem geneline
  yazma anlamına geldiği için kullanıcı onayı bekleniyor.
- `frontend/` ve `backend/` klasörleri **oluşturulmadı** — bunlar Aşama 1'in işi ve
  araçlar kurulmadan iskeletleri doğrulanamaz.
- README'nin "Kurulum ve çalıştırma" bölümü bilerek boş bırakıldı; çalıştığı
  doğrulanmamış komut yazılmadı.

### Sonraki adım

Aşama 1 (Frontend–Backend bağlantısı) — kullanıcının "devam" onayı ve
araç kurulumu izni bekleniyor.

---

## Aşama 1 — Frontend–Backend Bağlantısı · 2026-08-04 · ✅ Tamamlandı

### Kurulan araçlar

Kullanıcı onayıyla `brew install node python@3.12` çalıştırıldı.
Sistem Python 3.9'una dokunulmadı.

| Araç | Sürüm |
| --- | --- |
| Node.js | 26.6.0 |
| npm | 11.18.0 |
| Python | 3.12.13 (`/opt/homebrew/bin/python3.12`) |

### Backend

- `backend/.venv` sanal ortamı oluşturuldu, bağımlılıklar kuruldu.
- `app/core/config.py` — ayarlar tek yerde, ortam değişkenlerinden okunuyor.
- `app/core/logging.py` — log biçimi; ses içeriğinin loglanmayacağı not edildi.
- `app/api/health.py` — `GET /api/v1/health` → `{"status": "ok", "message": "Backend bağlantısı başarılı"}`
- `app/main.py` — CORS yalnızca `localhost:5173` ve `127.0.0.1:5173` için açık, wildcard yok.
- `requirements.txt` — ses kütüphaneleri bilerek eklenmedi (bkz. K-012).

### Frontend

- Vite + React 19 + TypeScript şablonu kuruldu, `strict` modu eklendi (K-013).
- `src/texts.ts` — tüm Türkçe kullanıcı metinleri tek dosyada (K-016).
- `src/api/client.ts` — hataları Türkçe mesaja çeviren fetch sarmalayıcısı (K-015).
- `src/hooks/useBackendHealth.ts` — bağlantı kontrolü, iptal desteği, tekrar deneme.
- `src/components/ConnectionStatus.tsx` — durum kartı, `role="status"`, metin etiketi (K-017).
- `src/App.tsx` — karşılama ekranı + teşhis olmadığı uyarısı + gizlilik açıklaması.
- `src/index.css` — CSS değişkenleri, açık/koyu tema, odak halkası, reduced-motion desteği.

### Testler — hepsi geçiyor

| Test | Sonuç |
| --- | --- |
| Backend (pytest) | ✅ 5/5 — health 200, cevap şeması, versiyonsuz `/health` 404, CORS izin/ret |
| Frontend (Vitest) | ✅ 6/6 — karşılama ekranı, uyarı metinleri, bağlantı başarılı/hatalı, tekrar dene |
| Tip kontrolü (`tsc -b`) | ✅ temiz |
| Lint (oxlint) | ✅ temiz |
| Üretim derlemesi (`vite build`) | ✅ başarılı |

### Tarayıcıda doğrulama

Her iki sunucu da çalıştırıldı ve http://localhost:5173 gerçekten açıldı:

- ✅ Bağlantı kartı "Backend bağlantısı başarılı" gösteriyor.
- ✅ Backend durdurulunca kart hataya geçiyor ve anlaşılır Türkçe mesaj veriyor
  (ham hata veya HTTP kodu sızmıyor).
- ✅ Backend geri açılınca bağlantı düzeliyor.
- ✅ Mobil (375px) ve masaüstü genişliğinde düzen bozulmuyor.
- ✅ Tarayıcı konsolunda hata/uyarı yok.

### Kabul kriterleri

| Kriter | Durum |
| --- | --- |
| Backend başlıyor | ✅ |
| Frontend başlıyor | ✅ |
| Health endpoint 200 dönüyor | ✅ |
| Frontend mesajı gösterebiliyor | ✅ |
| Konsolda kritik hata yok | ✅ |

### Açık kalan küçük iş

Vite şablonundan gelen kullanılmayan görseller (`src/assets/react.svg`, `vite.svg`,
`hero.png`, `public/icons.svg`) hâlâ duruyor. Dosya silmek için kullanıcı izni
gerektiğinden bırakıldı; onay verilirse temizlenecek.

### Sonraki adım

Aşama 2 (Mikrofon ve kayıt akışı) — kullanıcının "devam" onayı bekleniyor.

---

## Aşama 2 — Mikrofon ve Kayıt Akışı · 2026-08-05 · ✅ Tamamlandı

### Eklenen akış

Karşılama ekranından "Başla" ile giriş: Mikrofon Kontrolü → Test 1 (Konuşma) →
Test 2 (Uzun "A") → Test 3 (Kaydırma) → İnceleme ekranı. Her testten "İncelemeye
geç/dön" veya "Sonraki test" ile ilerlenir; inceleme ekranından herhangi bir teste
dönüp yeniden kaydettikten sonra otomatik olarak incelemeye geri dönülür.

### Yeni dosyalar

| Alan | Dosyalar |
| --- | --- |
| Ortak tipler | `src/types/recording.ts` (`TestId`, `RecordingResult`, `RecordingsState`) |
| Mikrofon | `features/microphone-check/useMicrophoneStream.ts`, `useMicrophoneLevel.ts`, `MicrophoneCheck.tsx` |
| Ses testleri | `features/voice-tests/testConfig.ts`, `useAudioRecorder.ts`, `VoiceTestScreen.tsx`, `RecordingsReview.tsx` |
| Karşılama | `features/onboarding/WelcomeScreen.tsx` (Aşama 1'deki içerik buraya taşındı) |
| Paylaşılan | `components/ScreenLayout.tsx`, `styles/buttons.css`, `utils/time.ts` |

### Kapsanan gereksinimler (CLAUDE.md Aşama 2)

- ✅ Mikrofon izni ekranı + tarayıcı desteği kontrolü (`getUserMedia`/`MediaRecorder` varlığı)
- ✅ Üç test ekranı, her biri test numarası/adı/talimat/örnek süre ile
- ✅ Kayıt başlatma, durdurma, süre sayacı, maksimum sürede otomatik durdurma
- ✅ Kaydı dinleme (`<audio controls>`), silme, yeniden kaydetme
- ✅ Üç kayıt tamamlanmadan "Analiz et" butonu pasif kalıyor
- ✅ Backend analizi henüz bağlanmadı — buton tıklanınca yalnızca "bir sonraki aşamada eklenecek" mesajı gösteriyor
- ✅ Aynı anda yalnızca bir kayıt yapılabiliyor (hook seviyesinde de korunuyor)
- ✅ Sayfa yenilenirse (kayıt varken) `beforeunload` uyarısı çıkıyor
- ✅ Kayıt, yalnızca kullanıcı butona bastığında başlıyor (otomatik başlamıyor)

### Testler — hepsi geçiyor

| Test | Sonuç |
| --- | --- |
| Frontend (Vitest) | ✅ **14/14** (Aşama 1'deki 6 test + yeni 8 test) |
| Tip kontrolü (`tsc -b`) | ✅ temiz |
| Lint (oxlint) | ✅ temiz |
| Üretim derlemesi (`vite build`) | ✅ başarılı |

Yeni testler: mikrofon izni reddedilince Türkçe hata mesajı gösterildiği
(sahte `DOMException`/`NotAllowedError` ile), kayıt başlatılıp durdurulunca
durumun değiştiği ve kaydın dinlenebilir hâle geldiği (sahte `MediaRecorder`
ile), üç kayıt tamamlanmadan/tamamlanınca "Analiz et" butonunun pasif/aktif
olduğu (`RecordingsReview.test.tsx`), `formatSeconds` yardımcı fonksiyonu.

### Tarayıcıda doğrulama

Gerçek tarayıcıda uçtan uca denendi: "Başla" ile Mikrofon Kontrolü ekranına
geçildi, "Mikrofona izin ver" butonuna basıldı. Test ortamında gerçek mikrofon
donanımı olmadığı için tarayıcı `NotFoundError` fırlattı — bu, hata haritalama
kodunun **gerçek bir hata senaryosunda** doğru çalıştığını kanıtladı: ekranda
"Mikrofon bulunamadı. Cihazında çalışan bir mikrofon olduğundan emin ol." mesajı
ve "Tekrar dene" butonu göründü, konsolda hata sızmadı. Gerçek kayıt (start/stop/
dinleme) adımı mikrofonlu bir cihaz gerektirdiği için burada denenemedi; bu akış
sahte `MediaRecorder` ile otomatik testte doğrulandı.

### Kabul kriterleri

| Kriter | Durum |
| --- | --- |
| Kullanıcı üç ayrı kaydı oluşturabiliyor | ✅ (kod + otomatik test; gerçek mikrofonla elle doğrulanmadı) |
| Kayıtları dinleyebiliyor | ✅ |
| Kayıtları ayrı ayrı yeniden yapabiliyor | ✅ |
| İzin reddi doğru yönetiliyor | ✅ (gerçek tarayıcıda doğrulandı) |

### Kullanıcı doğrulaması — 2026-08-05

Kullanıcı kendi tarayıcısında (gerçek mikrofonla) üç testi de tamamladı ve
ekran görüntüsüyle paylaştı: üç kayıt "KAYDEDİLDİ" durumunda, süreler 0:04 /
0:02 / 0:03, "Analiz et" butonu aktif hâle geldi. Yukarıdaki "doğrulanamayan
nokta" artık kapandı — uçtan uca kayıt akışı gerçek bir cihazda çalışıyor.

### Sonraki adım

Aşama 3 (Dosya yükleme ve kalite kontrolü) — kullanıcının "devam" onayı bekleniyor.

---

## Aşama 3 — Dosya Yükleme ve Kalite Kontrolü · 2026-08-05 · ✅ Tamamlandı

Bu aşama yalnızca backend'i kapsıyor (CLAUDE.md'de Aşama 3 için frontend
bağlantısı istenmiyor). "Analiz et" butonu hâlâ backend'e istek atmıyor; bu
Aşama 4/5'te bağlanacak. Henüz pitch/perde analizi yok — yalnızca kayıt kalitesi.

### Yeni bağımlılıklar

`av==18.0.0` (PyAV — ffmpeg kütüphanelerini pip paketinin içinde taşır, sisteme
ayrıca FFmpeg kurulmadı) ve `numpy==2.5.1`. İkisi de gerçek WebM/Opus dosyasıyla
denenip doğrulandı (bkz. K-023).

### Eklenen dosyalar

| Dosya | İçerik |
| --- | --- |
| `app/services/audio_conversion.py` | Herhangi bir ses formatını PyAV ile mono/22.050 Hz float diziye çevirir; çözülemeyen dosyayı `UnsupportedAudioError` ile işaretler |
| `app/services/audio_quality.py` | Süre, RMS, peak, clipping oranı, sessizlik oranı hesaplar; eşiklerle karşılaştırıp kabul/ret + 0-100 skor + Türkçe uyarı listesi üretir |
| `app/schemas/analysis.py` | `FileQualityReport`, `AnalyzeSessionResponse` Pydantic modelleri |
| `app/api/analysis.py` | `POST /api/v1/analyze-session` — üç dosyayı güvenli geçici dosyalara yazar, boyut sınırını akış sırasında denetler, her birini değerlendirir, işlem bitince (başarılı/başarısız fark etmez) geçici dosyaları siler |
| `app/core/config.py` | Süre/RMS/clipping/sessizlik eşikleri, hedef örnekleme oranı — hepsi açıklamalı sabitler |

### Kapsanan gereksinimler (CLAUDE.md Aşama 3)

- ✅ `POST /api/v1/analyze-session`, üç dosya multipart olarak alınıyor
- ✅ Format doğrulama gerçek çözümlemeyle yapılıyor (MIME/uzantıya güvenilmiyor, bkz. K-024)
- ✅ Dosya boyutu sınırı akış sırasında denetleniyor, aşılırsa 413
- ✅ Geçici dosyalar rastgele adlarla oluşturuluyor, işlem bitince (`finally` içinde) her zaman siliniyor
- ✅ Süre, sessizlik (RMS tabanlı pencere analizi), clipping oranı kontrol ediliyor
- ✅ Kötü kayıtlar CLAUDE.md'deki örnek Türkçe uyarı cümleleriyle reddediliyor (bkz. K-026)
- ⏸️ Arka plan gürültüsü tahmini eklenmedi — güvenilir biçimde yapmak pitch/voice-activity bilgisi gerektiriyor, bu Aşama 4'e bırakıldı

### Testler — hepsi geçiyor

| Test | Sonuç |
| --- | --- |
| Backend (pytest) | ✅ **13/13** (5 mevcut health testi + 8 yeni analiz testi) |

Yeni testler (`tests/test_analysis.py`, sentetik seslerle): geçerli kayıtların
kabul edilmesi, desteklenmeyen format reddi, çok kısa kayıt reddi, sessiz kayıt
reddi, bozuk/clip'li kayıt reddi, aşırı büyük dosyanın 413 ile reddi, geçici
dosyaların temizlendiğinin doğrulanması, response şemasının doğruluğu.

### Gerçek dosyayla doğrulama

Sentetik testlere ek olarak, gerçek tarayıcı formatına en yakın senaryo canlı
sunucuda elle denendi: PyAV ile kodlanmış 2 saniyelik bir WebM/Opus dosyası
`curl` ile üç alana da gönderildi. Sonuç doğru çıktı: konuşma ve kaydırma
testleri (minimum 3 saniye) reddedildi, uzun "A" testi (minimum 2 saniye) kabul
edildi — eşik mantığı gerçek bir ses dosyasıyla teyit edildi.

### Kabul kriterleri

| Kriter | Durum |
| --- | --- |
| Üç kayıt backend'e ulaşıyor | ✅ |
| Geçerli kayıt kabul ediliyor | ✅ |
| Geçersiz kayıt doğru reddediliyor | ✅ |
| Geçici dosyalar temizleniyor | ✅ (otomatik testle doğrulandı) |

### Sonraki adım

Aşama 4 (Ses analizi — pitch/nota tespiti) — kullanıcının "devam" onayı bekleniyor.

---

## Aşama 4 — Ses Analizi · 2026-08-05 · ✅ Tamamlandı

Bu aşama da yalnızca backend'i kapsıyor — sonuç ekranı yok (Aşama 5), "Analiz
et" butonu hâlâ backend'e istek atmıyor. Ama backend artık gerçek sayılar
üretiyor: nota tespiti, stabilite skoru, gözlemlenen aralık, tahmini profil.

### Yeni bağımlılıklar

`librosa==0.11.0`, `scipy==1.18.0`. SoundFile **eklenmedi** — ses zaten Aşama
3'te PyAV ile numpy dizisine çevrilmiş durumda, librosa.pyin bunu doğrudan
kabul ediyor (bkz. K-028, CLAUDE.md'nin belirttiği yığından bilinçli sapma).

### Eklenen dosyalar

| Dosya | İçerik |
| --- | --- |
| `app/services/music_theory.py` | Hz ↔ MIDI ↔ nota adı dönüşümü (standart MIDI formülü, A4=440 Hz) |
| `app/services/pitch_analysis.py` | `librosa.pyin` ile F0 çıkarımı, oktav hatası/düşük güven temizliği, üç test için ayrı analiz fonksiyonu, stabilite skoru |
| `app/services/profile_builder.py` | Glide aralığının orta noktasından kaba "merkez bölge" + "aralık genişliği" tahmini, Türkçe özet metni |
| `app/core/config.py` | pyin arama aralığı, sıçrama/güven eşikleri, stabilite skoru ağırlıkları, profil sınır değerleri — hepsi açıklamalı sabitler |

`app/api/analysis.py` ve `app/schemas/analysis.py` genişletildi: her testin
cevabına gerçek pitch alanları ve oturum geneline `quality` + `profile` eklendi.

### Kapsanan gereksinimler (CLAUDE.md Aşama 4)

- ✅ `librosa.pyin` ile F0 çıkarımı (arama aralığı ~C2-C7)
- ✅ Konuşma analizi (medyan F0, yaklaşık nota, perde değişkenliği, voiced oranı)
- ✅ Uzun "A" stabilite analizi (cents sapma, dropout, sıçrama sayısı, 0-100 skor)
- ✅ Glide aralık analizi (gözlemlenen alt/üst nota, tahmini rahat bölge — %5/%95 yüzdelik dilim, uç değerler doğrudan kullanılmıyor)
- ✅ Hz–MIDI–nota dönüşümü (standart formül, A4=440 Hz)
- ✅ Aykırı değer temizliği (düşük güvenli frame'ler + oktav hatası sıçramaları elenir; konuşmadaki gerçek hece geçişleri yanlışlıkla silinmez, bkz. K-029)
- ✅ Güven skoru (`confidence` — güvenilir frame oranı, açıkça "istatistiksel güven aralığı değildir" diye belirtiliyor)
- ✅ Tahmini profil oluşturma (klasik ses türü sınıflandırması değil, bkz. K-033)
- ✅ Otomatik sentetik ses testleri

### Testler — hepsi geçiyor

| Test dosyası | Sonuç |
| --- | --- |
| `test_health.py` | ✅ 5/5 |
| `test_analysis.py` | ✅ 12/12 (8 mevcut + 4 yeni: pitch alanları doluyor, profil üretiliyor ve tıbbi ifade içermiyor, reddedilen kayıtta pitch/profil None) |
| `test_pitch_analysis.py` | ✅ 8/8 (A3/C4 nota tespiti, stabil/dalgalanan stabilite karşılaştırması, sessizlikte uydurma yok, glide alt/üst nota, glide sessizlikte uydurma yok) |
| `test_profile_builder.py` | ✅ 6/6 (glide yoksa profil yok, düşük/yüksek/dar/geniş etiketleri, özet metninde kesin/tıbbi ifade veya klasik ses türü adı yok) |
| **Toplam** | **✅ 30/30** |

CLAUDE.md madde 15'teki sentetik ses testleri (220 Hz→A3, 261.63 Hz→C4, stabil/
dalgalanan sinüs, glide alt/üst nota) birebir karşılanıyor.

### Gerçek dosyayla doğrulama

Üç ayrı WebM/Opus dosyası (150 Hz konuşma, 196 Hz uzun ünlü, 98→330 Hz kaydırma
— CLAUDE.md'nin kendi G2-E4 örneğiyle aynı aralık) PyAV ile kodlanıp canlı
sunucuya `curl` ile gönderildi. Sonuç: `observed_low_note: "G2"`,
`observed_high_note: "E4"`, `range_semitones: 21` — CLAUDE.md'nin örnek
JSON'undaki değerlerle birebir eşleşti. Sabit tonlu kayıtta stabilite skoru
100, tahmini profil metni beklenen Türkçe cümle yapısında ve tıbbi/kesin ifade
içermiyor.

### Kabul kriterleri

| Kriter | Durum |
| --- | --- |
| A3 ve C4 sentetik testleri kabul edilebilir toleransta doğru bulunuyor | ✅ |
| Sessiz veya anlamsız ses için nota uydurulmuyor | ✅ |
| Üç test için response schema doluyor | ✅ |
| Düşük güvenli sonuç açıkça işaretleniyor | ✅ (`confidence` alanı + kalite reddinde pitch alanları boş) |

### Sonraki adım

Aşama 5 (Sonuç ekranı) — kullanıcının "devam" onayı bekleniyor.

---

## Aşama 5 — Sonuç Ekranı · 2026-08-05 · ✅ Tamamlandı

"Analiz et" butonu ilk kez gerçekten backend'e istek atıyor. Karşılama →
Mikrofon → 3 test → İnceleme → **Analiz ediliyor → Sonuç ekranı** akışı artık uçtan uca tam.

### Eklenen dosyalar

| Dosya | İçerik |
| --- | --- |
| `types/analysis.ts` | Backend'in `AnalyzeSessionResponse` şemasıyla birebir eşleşen TypeScript tipleri |
| `api/analysis.ts` | Üç kaydı tek multipart istekte `/analyze-session`'a gönderir |
| `api/client.ts` | `apiPostForm` eklendi (JSON POST değil, FormData — Content-Type tarayıcıya bırakılıyor) |
| `features/analysis/AnalyzingScreen.tsx` | Sahte yüzde göstergesi yerine gerçek aşama mesajları (bkz. K-034) |
| `features/analysis/ResultsScreen.tsx` | Backend JSON'unu Türkçe kartlara çeviren asıl sonuç ekranı |

`App.tsx` genişletildi: `analyzing`/`results` adımları, hata/tekrar dene akışı,
"Testi yeniden yap" ile tam sıfırlama. `RecordingsReview`'daki eski "yakında
eklenecek" yer tutucusu kaldırıldı (artık gerçek işlevsellik var).

### Kapsanan gereksinimler (CLAUDE.md Aşama 5)

- ✅ Tahmini ses profili, gözlemlenen nota aralığı, tahmini rahat bölge
- ✅ Konuşma perdesi, stabilite, sesli süre, kayıt kalitesi, güven skoru
- ✅ Açıklama metni (backend'in ürettiği profil özeti)
- ✅ Profesyonel teşhis olmadığı uyarısı (her sonuç ekranında)
- ✅ Testi yeniden yapma
- ✅ Teknik JSON kullanıcı dostu Türkçe kartlara çevriliyor
- ✅ Düşük güven durumları doğru anlatılıyor ("Bu sonucun güveni düşük; temkinli yorumla.")
- ✅ Kesin veya tıbbi iddia kullanılmıyor (testle doğrulanıyor)
- ✅ Mobil ekranlarda düzgün görünüyor (tarayıcıda elle doğrulandı)

### Bulunan ve düzeltilen gerçek hata

Tarayıcıda uçtan uca denerken (bkz. aşağıdaki "Tarayıcıda doğrulama" bölümü),
mikrofon seviye göstergesinin (`useMicrophoneLevel`) `AudioContext` kurulumu
başarısız olduğunda **tüm uygulamayı** boş bir sayfaya düşürdüğü ortaya çıktı —
küçük bir görsel özelliğin tüm akışı çökertmesi kabul edilemezdi. `try/catch`
ile düzeltildi, regresyon testi eklendi. Detay: K-037.

### Testler — hepsi geçiyor

| Test dosyası | Sonuç |
| --- | --- |
| Mevcut testler (Aşama 1-4) | ✅ 14/14 |
| `AnalyzingScreen.test.tsx` | ✅ 1/1 |
| `ResultsScreen.test.tsx` | ✅ 8/8 (veri→kart eşlemesi, profil/aralık yoksa uydurmuyor, düşük güven notu, kesin/tıbbi ifade yok, reddedilen oturum, yeniden başlatma) |
| `useMicrophoneLevel.test.ts` | ✅ 2/2 (K-037 regresyon testi dahil) |
| App uçtan uca analiz testi | ✅ 1/1 (üç test kaydedilip "Analiz et"e basılınca backend verisi doğru kartlara yerleşiyor, ham alan adları sızmıyor) |
| **Toplam** | **✅ 26/26** |

Tip kontrolü, lint ve üretim derlemesi temiz.

### Tarayıcıda doğrulama

Gerçek tarayıcıda (bu ortamda gerçek mikrofon donanımı olmadığından
`fetch`/`getUserMedia`/`MediaRecorder` yalnızca doğrulama amacıyla geçici
olarak taklit edilerek — kaynak kod değiştirilmeden) uçtan uca denendi:

- ✅ Üç test gerçekten kaydedilip (gerçek zaman geçirilerek) inceleme ekranına ulaşıldı
- ✅ "Analiz et" → "Analiz ediliyor" → Sonuç ekranı geçişi çalıştı
- ✅ Sonuç ekranı masaüstünde: profil özeti, 2 sütunlu kart grid'i, düşük güven notları doğru kartlarda (Gözlemlenen Nota Aralığı, Analiz Güven Skoru) — bilerek düşük confidence (0.35) gönderildi
- ✅ Mobilde (375px): tek sütun, hiçbir taşma/kesme yok
- ✅ Konsolda hata yok (K-037 düzeltmesinden sonra)
- ⏸️ Reddedilen oturum senaryosu tarayıcıda elle denenmedi (görsel karmaşıklığı düşük — tek uyarı listesi + buton); `ResultsScreen.test.tsx`'te otomatik testle doğrulandı

### Kabul kriterleri

| Kriter | Durum |
| --- | --- |
| Teknik JSON kullanıcı dostu Türkçe kartlara çevriliyor | ✅ |
| Düşük güven durumları doğru anlatılıyor | ✅ |
| Kesin veya tıbbi iddia kullanılmıyor | ✅ |
| Mobil ekranlarda düzgün görünüyor | ✅ |

### Sonraki adım

Aşama 6 (Şarkı önerileri) — kullanıcının "devam" onayı bekleniyor.

---

## Aşama 6 — Şarkı Önerileri · 2026-08-05 · ✅ Tamamlandı

Şarkı önerileri artık `POST /api/v1/analyze-session` cevabının bir parçası
(CLAUDE.md'nin örnek şemasıyla birebir uyumlu — ayrı bir uç nokta değil, bkz.
K-038). Sonuç ekranında "Analiz et"e basınca ilk kez öneri kartları da görünüyor.

### Eklenen dosyalar

| Dosya | İçerik |
| --- | --- |
| `backend/app/data/demo_songs.json` | 12 açıkça kurgu "Demo Şarkı" kaydı (`verified: false`), farklı aralık/zorluk/tür karışımı |
| `backend/app/services/recommendation.py` | Şarkı yükleme, aralık eşleştirme, ton değiştirme önerisi, 0-100 skor, sıralama |
| `frontend/src/features/analysis/SongRecommendations.tsx` | Öneri kartları + zorluk filtresi (Tümü/Kolay/Orta/Zor) |

`backend/app/services/pitch_analysis.py`'deki `GlideAnalysis`'e
`estimated_comfortable_low_midi`/`high_midi` eklendi (öneri eşleştirmesi bu
sayısal değerleri kullanıyor; nota adı string'inden geri MIDI'ye çevirmiyor).
`schemas/analysis.py` ve `api/analysis.py` `recommendations` alanını
kapsayacak şekilde genişletildi.

### Kapsanan gereksinimler (CLAUDE.md Aşama 6)

- ✅ Şarkı veri modeli (id, title, artist, language, genre, min/max_midi,
  min/max_note, difficulty, verified, source_note, optional_transposition_limit)
- ✅ JSON içe aktarma (`demo_songs.json`, `lru_cache` ile bir kez okunuyor)
- ✅ Aralık eşleştirme algoritması: gözlemlenen aralık örtüşmesine göre 0-100 skor
- ✅ Ton değiştirme önerisi: 1-3 yarı ton taşan şarkılar için (−3..+3 arası en
  az taşmayı veren kaydırma brute-force bulunuyor, bkz. K-039)
- ✅ Çok büyük fark varsa şarkı filtrelenmiyor, düşük skorla geride kalıyor
- ✅ Zorluk seviyesi skora dahil (backend) + ayrı filtre kontrolü (frontend, K-040)
- ✅ En uygun 5-10 sonuç sıralanıyor (`MAX_RECOMMENDATIONS = 10`)
- ✅ Öneri kartı: şarkı adı, sanatçı, tür, zorluk, nota aralığı, eşleşme
  yüzdesi, gerekirse "N semiton aşağıdan/yukarıdan denemek daha rahat
  olabilir" uyarısı
- ✅ Gerçek şarkı aralıkları uydurulmuyor — yalnızca demo veri, `verified: false`,
  frontend'de görünür "Demo veri" rozeti (K-042)

### Testler — hepsi geçiyor

| Test dosyası | Sonuç |
| --- | --- |
| Mevcut backend testleri | ✅ 32/32 |
| `test_recommendation.py` | ✅ 14/14 (tam sığma, 2 yarı ton taşma → doğru yönde ton önerisi, aşırı taşma → öneri yok + düşük skor, zorluk skoru düşürüyor, şarkıya özel transposition sınırına uyuluyor, skor asla negatif değil, tutarlı sonuçlar, sıralama, aralık değişince sıralama değişiyor, demo şarkılar hiç `verified` işaretlenmiyor, açıkça kurgu isimler, en fazla 10 sonuç) |
| `test_analysis.py` (yeni testler) | ✅ (kabul edilen oturumda öneri üretiliyor + sıralı; reddedilen oturumda öneri yok) |
| Mevcut frontend testleri | ✅ 26/26 |
| `ResultsScreen.test.tsx` (yeni testler) | ✅ 6/6 (öneri yoksa bölüm gizli, kart alanları doğru, demo rozeti, aşağı/yukarı ton ipucu, zorluk filtresi) |
| App uçtan uca testi (genişletildi) | ✅ (öneri bölümü de kontrol ediliyor) |
| **Backend toplam** | **✅ 46/46** |
| **Frontend toplam** | **✅ 32/32** |

Tip kontrolü, lint ve üretim derlemesi temiz.

### Gerçek dosyayla ve tarayıcıda doğrulama

- Gerçek WebM/Opus dosyalarıyla canlı sunucuya istek atıldı: 10 öneri, doğru
  sıralı (100, 100, 100, 95, 95, 95, 87, 84, 63, 34), ton önerileri doğru
  yönde (`-3`, `2` gibi), hepsi `verified: false`.
- Tarayıcıda (fetch/mikrofon API'leri yalnızca doğrulama amaçlı taklit
  edilerek) uçtan uca denendi: üç test kaydedildi, "Analiz et"e basıldı,
  sonuç ekranında "Şarkı önerileri" bölümü doğru verilerle göründü.
- Masaüstünde ve mobilde (375px): kartlar tek sütun, "Demo veri" rozeti
  belirgin, transposition ipuçları doğru metinle görünüyor.
- Zorluk filtresi elle denendi: "Zor"a basınca liste 4 şarkıdan 1'e düştü
  (yalnızca zor olan kaldı), "Tümü"ne dönünce 4'ü de geri geldi.
- Konsolda hata yok.

### Kabul kriterleri

| Kriter | Durum |
| --- | --- |
| Demo verilerden tutarlı öneriler çıkıyor | ✅ |
| Kullanıcı aralığı değişince sıralama değişiyor | ✅ |
| Ton önerisi matematiksel olarak doğru hesaplanıyor | ✅ |
| Demo veriler gerçek/verifiye edilmiş şarkı gibi sunulmuyor | ✅ |

### Sonraki adım

Aşama 7 (Kalite, test ve dokümantasyon) — kullanıcının "devam" onayı bekleniyor.

---

## Aşama 7 — Kalite, Test ve Dokümantasyon · 2026-08-05 · ✅ Tamamlandı

Bu aşamada yeni bir özellik eklenmedi; mevcut altı aşama gözden geçirildi,
temizlendi ve belgelendi.

### Yapılanlar

**Bağımlılık denetimi:**
- `scipy`'nin gerçekten gerekli olup olmadığı test edildi (kaldırılıp
  paket çalıştırıldı) — `librosa.pyin` çalışma zamanında ona ihtiyaç
  duyuyor, geri kuruldu ve neden orada olduğu yorumla netleştirildi (K-043).
- `httpx`'in neden `requirements.txt`'de olduğu netleştirildi (FastAPI
  TestClient'ın arka planda kullandığı kütüphane).
- Frontend bağımlılıkları (`package.json`) tarandı — kullanılmayan paket
  bulunmadı.

**Kod temizliği (kullanıcı onayıyla):**
- Vite şablonundan kalan, hiçbir yerde kullanılmayan 5 dosya silindi:
  `src/assets/react.svg`, `vite.svg`, `hero.png`, `public/icons.svg`,
  `frontend/README.md` (K-044). Build ve testler sonrasında doğrulandı.

**Erişilebilirlik:**
- Başlık hiyerarşisi (`h1` → `h2` → `h3`) tüm ekranlarda tutarlı bulundu.
- Kayıt/inceleme ekranlarındaki `<audio>` elemanlarına ayırt edici
  `aria-label` eklendi — birden fazla oynatıcı aynı ekranda olduğunda hangi
  testin kaydı olduğu artık ekran okuyucuya da bildiriliyor (K-045).
- Tab ile odaklanma sırası ve `:focus-visible` halkası tarayıcıda görsel
  olarak doğrulandı.
- Klavye ile buton aktivasyonu (Enter/Space) bu ortamda kesin olarak
  doğrulanamadı — ayrıntı ve gerekçe için K-046'ya bakın. Kodda engelleyici
  yok, ama dürüstçe "doğrulanamadı" olarak işaretlendi.

**Hata durumları:**
- Backend'in beklenmeyen hatalarda (500) stack trace veya dosya yolu
  sızdırmadığı doğrulandı — `UnsupportedAudioError`'ın ham mesajı hiçbir
  zaman API cevabına yazılmıyor, FastAPI `debug=False` varsayılanında çalışıyor.
- Daha önce hiç test edilmemiş bir senaryo bulundu ve kapatıldı: **analiz
  isteği sırasında** (health check değil) sunucu hatası olursa ne oluyordu?
  Yeni test (`Analiz sırasında hata durumu`) bunu kapsıyor: anlaşılır Türkçe
  mesaj gösteriliyor, ham HTTP kodu sızmıyor, "İncelemeye dön" kayıtları
  koruyarak geri götürüyor, "Tekrar dene" mekanizması çalışıyor.

**Dokümantasyon:**
- README.md: Teknoloji/Gereksinimler tabloları güncel duruma göre düzeltildi
  (SoundFile kaldırıldı, FFmpeg'in artık gerekmediği netleştirildi).
- README.md: **Bilinen sınırlamalar** bölümü eklendi (7 madde).
- README.md: **Manuel test kontrol listesi** eklendi (17 madde) — otomatik
  testlerin kapsamadığı, yalnızca gerçek tarayıcı/mikrofonla doğrulanabilecek
  şeyler için.
- Kurulum ve çalıştırma komutları README'de yazıldığı gibi tekrar
  çalıştırılıp doğrulandı (backend + frontend gerçekten ayağa kalktı, health
  check 200 döndü).

### Testler — final durum

| | Sonuç |
| --- | --- |
| Backend (pytest) | ✅ **46/46** |
| Frontend (Vitest) | ✅ **33/33** (1 yeni: analiz sırasında sunucu hatası + kurtarma) |
| Tip kontrolü, lint, üretim derlemesi | ✅ temiz |

### Manuel doğrulama

Kayıt akışının gerçek bir mikrofonla çalıştığı zaten Aşama 2'de kullanıcı
tarafından doğrulanmıştı. Bu aşamada ayrıca:
- Klavye ile Tab sırası ve odak halkası tarayıcıda görsel olarak kontrol edildi.
- Kurulum komutları sıfırdan çalıştırılıp health check doğrulandı.

### Doğrulanamayan / açık noktalar

- Enter/Space ile buton aktivasyonu bu otomasyon ortamında test edilemedi
  (K-046). Kod tarafında engelleyici yok; gerçek bir tarayıcıda çalışması
  beklenir ama kanıtlanamadı — README'nin manuel kontrol listesine eklendi.
- Renk kontrastı için otomatik bir araç (ör. axe) çalıştırılmadı; yalnızca
  görsel/manuel değerlendirme yapıldı (koyu tema, yüksek kontrastlı metin
  renkleri kullanıldı).

### Genel proje durumu

CLAUDE.md'nin planladığı 8 aşamadan 7'si tamamlandı. Uygulama uçtan uca
çalışıyor: mikrofon izni → 3 test kaydı → gerçek pitch analizi → tahmini ses
profili → demo şarkı önerileri. Backend 46, frontend 33 otomatik testle
kaplı; tip kontrolü ve lint temiz. Kalan tek aşama olan **Aşama 8 (Yayına
hazırlık)**, CLAUDE.md gereği yalnızca kullanıcının ayrıca açık onayıyla
başlar — production ortam değişkenleri, deploy, HTTPS, rate limiting gibi
konuları kapsıyor ve bu proje henüz o noktada değil (hâlâ tamamen yerel
geliştirme aşamasında).

### Sonraki adım

Aşama 8 (Yayına hazırlık) — yalnızca kullanıcı ayrıca ve açıkça onay verirse
başlanacak. Onay gelmezse proje mevcut hâliyle (Aşama 7 sonu) tamamlanmış sayılır.

---

## Gerçek şarkı verisi — 2026-08-05 · ✅ Tamamlandı

Aşama 6'da bilinçli olarak ertelenen ("gerçek şarkı listesi daha sonra
doğrulanmış verilerle eklenecektir") iş, kullanıcı isteğiyle şimdi yapıldı.
Bu, planın 8 aşamasından hiçbirine bağlı değil — bağımsız bir iş.

### Yapılanlar

`singingcarrots.com` (halka açık vokal aralığı veritabanı) üzerinde araştırma
yapılıp **16 gerçek şarkı** bulundu, her biri gösterilebilir bir kaynak
URL'iyle `backend/app/data/verified_songs.json`'a eklendi (`verified: true`).
`recommendation.py`'nin `load_songs()` fonksiyonu artık demo (12) ve gerçek
(16) şarkıları birleştirip tek bir havuzda (28 şarkı) puanlıyor.

**Kapsanan şarkılar:** Johnny Cash (I Walk the Line, Folsom Prison Blues),
Elvis Presley (Can't Help Falling in Love), Nat King Cole (Autumn Leaves),
Rufus Wainwright (Hallelujah), Marvin Gaye (Ain't No Mountain High Enough),
Linkin Park (What I've Done), Ed Sheeran (Shape of You, Perfect), Halsey
(Colors), Adele (Rolling in the Deep, Someone Like You), Celine Dion (My
Heart Will Go On), Celtic Woman (You Raise Me Up), Wings (Mull of Kintyre),
Queen (Bohemian Rhapsody).

### Açıkça belirtilmesi gereken sınırlama

**Türkçe şarkı bulunamadı.** Kullanılan kaynak (singingcarrots.com) Batı
müziği ağırlıklı; Türkçe şarkılar için hiçbir arama sonuç vermedi. Kullanıcı
onayıyla ("kaynak yoksa atla") bu boşluk uydurma veriyle doldurulmadı — 16
şarkının hepsi İngilizce (`language: "en"`). Türkçe gerçek şarkı eklemek
istenirse ayrı, güvenilir bir Türkçe kaynak bulunması gerekiyor.

### Veri dürüstlüğü

- Her şarkının `source_note` alanı gerçek bir URL içeriyor (test:
  `test_every_verified_song_is_marked_verified_with_a_real_source`)
- Zorluk seviyesi, kaynakta sayısal olarak bulunamadığı için nota aralığı
  genişliğinden şeffaf bir kuralla hesaplandı — bu `source_note`'ta açıkça
  belirtildi (K-048)
- Hiçbir şarkı hafızadan/tahminden eklenmedi

### Testler

| Test dosyası | Sonuç |
| --- | --- |
| Mevcut testler | ✅ 46/46 (1 test güncellendi — artık `verified: true` öneri de gelebileceği için) |
| `test_recommendation.py` (yeni `TestVerifiedSongs` sınıfı) | ✅ 5/5 (en az 1 gerçek şarkı var, her birinin gerçek kaynağı var, aralıklar tutarlı, havuz doğru birleşiyor, gerçek şarkı üst sıralarda çıkabiliyor) |
| **Backend toplam** | **✅ 51/51** |

Frontend'de hiçbir değişiklik gerekmedi — "Demo veri" rozeti zaten `verified`
alanına göre otomatik gösteriliyor/gizleniyordu (K-042), gerçek şarkılarda
kendiliğinden görünmüyor.

### Gerçek dosyayla doğrulama

Canlı sunucuya gerçek bir WebM dosyasıyla istek atıldı: cevapta hem demo hem
gerçek şarkılar (Elvis Presley, Nat King Cole, Marvin Gaye, Ed Sheeran) karışık
ve doğru skorla sıralı geldi.

### Sonraki adım

Aşama 8 (Yayına hazırlık) — hâlâ yalnızca ayrıca açık onayla başlanacak.

---

## Proje durdu — kullanıcı kararı · 2026-08-06

Kullanıcıya Aşama 8'e mi geçileceği yoksa burada mı durulacağı soruldu.
**Karar: burada durulsun, uygulama kendi bilgisayarında kullanılacak.**
Proje Aşama 7 + gerçek şarkı verisi ile tamamlanmış sayılıyor. Aşama 8
(yayına hazırlık: production ortamı, HTTPS, deploy) başlatılmadı; ileride
kullanıcı isterse ayrıca talep etmesi yeterli.

---

## Gerçek kullanım sırasında bulunan hata düzeltildi — 2026-08-06

Kullanıcı uygulamayı kendi mikrofonuyla denerken bir kayıtta ("F5-C#6", %5
güven, kaydırma testinin tahmini rahat bölgesi belirlenemedi) sonuç ekranında
"Şarkı önerileri" bölümünün hiç görünmediğini fark etti ve nedenini sordu.

**Kök neden:** Öneri, yalnızca kaydırma testinin tahmini rahat bölgesi
güvenilir şekilde hesaplanabildiyse üretiliyor (K-038 gereği doğru davranış —
uydurma öneri yapılmıyor). Ama arayüz bu durumda bölümü **hiçbir açıklama
olmadan** sessizce gizliyordu; kullanıcı "neden yok" diye anlayamadı.

**Düzeltme:** `ResultsScreen`, öneri listesi boşsa artık nedenini açıklayan
bir kutu gösteriyor: hangi testin (kaydırma) güvenilir sonuç vermediğini ve
nasıl daha iyi bir kayıt yapılabileceğini anlatıyor (bkz. K-050).
33/33 frontend testi (1 güncellendi) geçiyor, tarayıcıda kullanıcının
paylaştığı senaryo taklit edilerek doğrulandı.

---

## Aşama 8 — Yayına Hazırlık · 2026-08-06 · 🚧 Kod hazır, canlı deploy kullanıcı eylemi bekliyor

Kullanıcı, daha önce (aynı gün) verdiği "burada durulsun, lokal kalsın"
kararını değiştirip Aşama 8'e geçmeye karar verdi ve gerçek internet yayını
(ücretsiz katman PaaS) istediğini açıkça belirtti. Bu, CLAUDE.md'nin "proje
tamamen lokal çalışır" kuralıyla çeliştiği için önce o kural güncellendi
(bkz. K-051) — geri kalan tüm kısıtlar (hesap/veritabanı/ödeme/harici AI
API/Docker/Supabase yok) aynen korunarak.

### Yapılanlar

**Prod-güvenli varsayılanlar:**
- `backend/app/core/config.py`: `Settings.debug` varsayılanı `True`'dan
  `False`'a çevrildi (K-052) — ayarlanmamış bir ortamda güvenli log
  seviyesi sağlar; FastAPI'nin traceback sızıntısıyla ilgisi yok, o zaten
  hiçbir zaman `debug`'a bağlı değildi (Aşama 7'de doğrulanmıştı).
- CORS (`SESTINY_ALLOWED_ORIGINS`) ve upload limiti zaten env-var tabanlıydı,
  değişiklik gerekmedi — yalnızca gerçek deploy değerleri README'ye eklendi.

**Hız sınırlama (K-053):**
- `backend/app/core/rate_limit.py` (yeni): `slowapi` ile IP başına bellek
  içi sayaç, 429'da ham hata sızdırmayan Türkçe mesaj.
- `analyze-session` uç noktasına `ANALYZE_SESSION_RATE_LIMIT = "5/minute"`
  (config.py'de merkezi, açıklamalı sabit) uygulandı.
- `backend/tests/conftest.py` (yeni, projede ilk `conftest.py`): her testten
  önce limiter'ı sıfırlayan `autouse` fixture — aksi hâlde tüm test
  dosyaları aynı sahte IP'yi paylaştığı için birbirini 429'a düşürürdü.
- Frontend: `texts.errors.rateLimited` + `client.ts`'te 429'un ayrı
  yakalanması, ham HTTP kodu değil anlaşılır Türkçe mesaj gösteriyor.

**Deploy hazırlığı:**
- `backend/runtime.txt`: `python-3.12.13` (doğrulanmış sürümle aynı).
- Repo kökünde `render.yaml`: Render Blueprint (backend web servisi,
  build/start komutları, env var'lar). Render'ın panel alan adlarının
  gelecekte değişebileceği açıkça not edildi — README'deki manuel değerler
  asıl referans.
- `README.md`: yeni "Yayına alma (deploy)" bölümü — Render + Vercel için
  numaralı, kopyala-yapıştır kontrol listesi (deploy sırası: önce frontend,
  sonra backend'e gerçek frontend URL'i, sonra frontend'i gerçek backend
  URL'iyle yeniden build). "Gizlilik" bölümü, deploy edilirse ses kaydının
  artık yalnızca kendi bilgisayarda değil seçilen hosting'e (HTTPS
  üzerinden, kalıcı saklanmadan) gideceğini açıkça belirtecek şekilde
  güncellendi.
- `CLAUDE.md`, `docs/PROJECT_PLAN.md`, `docs/DECISIONS.md` (K-051 – K-055)
  güncellendi.

### Testler — tüm mevcut testler + yeniler geçiyor

| Test | Sonuç |
| --- | --- |
| Backend (pytest) | ✅ **55/55** (52 mevcut + `test_config.py` 1 + `test_rate_limit.py` 3 yeni; hiçbir mevcut test rate-limit fixture'ı olmadan bozulmadı) |
| Frontend (Vitest) | ✅ **34/34** (33 mevcut + 1 yeni: 429 durumunda anlaşılır mesaj) |
| Tip kontrolü, lint, üretim derlemesi | ✅ temiz |

### Yerel "production-mode" doğrulama (benim yapabildiğim kısım)

Gerçek hesap gerektirmeyen, yerelde çalıştırılabilen adımlar bizzat
denendi:

- Backend `SESTINY_DEBUG=false SESTINY_ALLOWED_ORIGINS=<gerçek-benzeri-URL>`
  ile `0.0.0.0:8000`'de başlatıldı: log seviyesi INFO (ayrıntılı değil),
  `/api/v1/health` 200 döndü.
- Bilinmeyen bir origin'den (`http://kotu-site.example`) istek atıldığında
  `access-control-allow-origin` başlığı **yok** — CORS gerçek prod-benzeri
  bir env var değeriyle de doğru çalışıyor.
- `curl` ile art arda 6 gerçek istek atıldı: ilk 5'i 200, 6.'sı tam olarak
  beklenen Türkçe mesajla 429 döndü.
- `VITE_API_BASE_URL=http://127.0.0.1:8000` ile **gerçek üretim derlemesi**
  (`npm run build`, dev server değil) alınıp `npm run preview` ile
  sunuldu; tarayıcıda (Browser pane) açılıp doğrulandı:
  - Backend'in izin listesinde `localhost:4173` yokken CORS isteği doğru
    şekilde reddetti (ekranda "Bağlanamadı").
  - Backend'e izin verilince ekranda "SUNUCU BAĞLANTISI: BAĞLI / Backend
    bağlantısı başarılı" göründü — derlenmiş bundle'ın `VITE_API_BASE_URL`'i
    doğru gömdüğü ve gerçek prod-mode backend'e bağlandığı kanıtlandı
    (ekran görüntüsüyle doğrulandı).

### Doğrulanamayan / açık noktalar (dürüstçe belirtilir, CLAUDE.md gereği)

- Hız sınırlamanın zaman penceresi dolunca gerçekten sıfırlandığı test
  edilmedi (freezegun gibi bir zaman taklit aracı gerekir, projede yok) —
  yalnızca eşiğin aşılınca 429 verdiği doğrulandı.

### Kabul kriterleri

| Kriter | Durum |
| --- | --- |
| Prod-güvenli varsayılanlar (debug kapalı) | ✅ |
| CORS gerçek origin'e ayarlanabilir, bilinmeyeni reddediyor | ✅ (yerel prod-mode ile doğrulandı) |
| Hız sınırlama çalışıyor ve test ediliyor | ✅ |
| Deploy manifestleri ve README kontrol listesi mevcut | ✅ |
| Gerçek canlı URL'ler çalışıyor | 🚧 Frontend canlı; backend düzeltme sonrası yeniden deploy bekliyor |

---

## Aşama 8 — Gerçek Deploy Denemesi · 2026-08-06

Kullanıcı, README'deki "Yayına alma" adımlarını kendi hesaplarıyla canlıda
denedi — projenin ilk gerçek üçüncü parti altyapı denemesi. Kod tarafında
öngörülemeyen bir hata bulundu ve düzeltildi (bkz. K-056).

### Yapılanlar

- **GitHub:** Kullanıcı `github.com/burakcankaplan0/sestiny` deposunu
  oluşturdu, kod push edildi (`main` dalı, commit `e55eeca`).
  - Küçük bir güvenlik notu: kullanıcı push için oluşturduğu geçici erişim
    anahtarını (token) sohbette paylaştı. Anahtar tek seferlik push için
    kullanılıp hiçbir dosyaya/`git` ayarına kalıcı yazılmadan hemen
    temizlendi; kullanıcıya anahtarı GitHub'dan iptal etmesi önerildi
    (kullanıcı bilinçli olarak "kalsın" dedi — kendi hesabı, kendi kararı).
- **Vercel (frontend):** Kullanıcı GitHub ile giriş yapıp `sestiny`
  deposunu içe aktardı, Root Directory `frontend` olarak ayarlandı,
  `VITE_API_BASE_URL` geçici bir değerle deploy edildi. **Başarılı** —
  frontend artık gerçekten canlı: **`https://sestiny.vercel.app`**
- **Render (backend):** Kullanıcı Blueprint ile (`render.yaml` otomatik
  algılandı) `sestiny-backend` servisini oluşturdu, `SESTINY_ALLOWED_ORIGINS`
  değerini gerçek Vercel adresine ayarladı. **İlk build başarısız oldu.**

### Bulunan gerçek hata: `requirements.txt`'teki numpy pini yanlıştı

Render'ın build log'u incelenince kök neden bulundu: `requirements.txt`
`numpy==2.5.1` diyordu, ama bu tarihe kadar hiç fark edilmemiş bir şekilde
yerelde (ve tüm 55 testin geçtiği ortamda) gerçekte kurulu olan sürüm
`numpy==2.4.6` idi. Render bu farkı hemen ortaya çıkardı: pip, pinlenen
2.5.1'e uygun bir `numba` (librosa'nın kullandığı bir kütüphane) sürümü
ararken geriye doğru arama yapıp Python 3.12'yi desteklemeyen çok eski bir
numba sürümüne düştü ve build çöktü. **Bu, yerel geliştirme ortamının hiçbir
zaman sıfırdan yeniden kurulmamasının gizlediği bir hataydı** — canlı deploy
denemesi olmasaydı fark edilmeyecekti.

**Düzeltme:** `numpy` pini gerçek/test edilen sürüme (`2.4.6`) düzeltildi,
`numba==0.66.0` ve `llvmlite==0.48.0` da açıkça pinlendi (bkz. K-056).
Düzeltme, sıfırdan bir `.venv` ile (Render'ın yapacağı gibi) yerel olarak
yeniden denendi: kurulum hiç geri arama yapmadan direkt doğru sürümlere
indi, **55/55 test bu temiz ortamda da geçti**. Değişiklik commit'lenip
push edildi — Render'ın bu düzeltmeyle otomatik olarak yeniden build
etmesi bekleniyor.

### Şu anki durum

| Bileşen | Durum |
| --- | --- |
| Frontend (Vercel) | ✅ Canlı — `https://sestiny.vercel.app` |
| Backend (Render) | ✅ Canlı — `https://sestiny-backend.onrender.com`, düzeltme sonrası build başarılı |
| CORS (iki gerçek origin arasında) | ✅ Doğrulandı — Vercel adresi izinli, bilinmeyen origin reddediliyor |
| Uçtan uca (gerçek internetten) | ✅ Doğrulandı — bkz. aşağıda |

Yayına almanın son adımında bir eksik daha bulundu: `render.yaml`'daki
`SESTINY_ALLOWED_ORIGINS` (`sync: false`) Blueprint kurulumunda hiç
otomatik alan olarak görünmemiş, kullanıcı bunu Render'ın Environment
sekmesinden elle eklemek zorunda kaldı (README'de bu adım zaten vardı, ama
Blueprint akışında hatırlatma olmadığı ilk seferde atlanmasına yol açtı).
Eklenince CORS `curl` ile doğrulandı: Vercel origin'i `access-control-allow-origin`
başlığı alıyor, bilinmeyen origin almıyor.

**Vercel `VITE_API_BASE_URL` güncellendi ve yeniden deploy edildi.**
Derlenmiş JS paketi kontrol edildi: gerçek backend adresi (`sestiny-backend.onrender.com`)
gömülü, eski geçici adres (`127.0.0.1`) kalmamış. Tarayıcıda gerçek canlı
adres (`https://sestiny.vercel.app`) açılıp doğrulandı: "SUNUCU BAĞLANTISI:
BAĞLI / Backend bağlantısı başarılı" görünüyor, konsolda hata yok
(ekran görüntüsüyle kanıtlandı).

### Uçtan uca gerçek kullanıcı testi — tamamlandı

Kullanıcı, adresi kendi telefonuna gönderip gerçek mikrofonuyla tüm akışı
(mikrofon izni → 3 test kaydı → analiz → sonuç ekranı) canlı adres
üzerinden denedi. Sonuç: analiz tamamlandı (backend'in Render'ın ücretsiz
katmanında "uyanması" + gerçek analiz nedeniyle ~1 dakika sürdüğü
gözlemlendi — bu, aşağıdaki performans notuyla tutarlı, bir hata değil).
Sonuç ekranı doğru Türkçe kartlarla geldi: "Orta-Düşük Merkezli Ses
Profili", gözlemlenen aralık F#2–A#2 (4 yarı ton), %4 analiz güveni ile
düşük güven uyarısı, ve **şarkı önerisi bölümü boş çıktığında nedenini
açıklayan kutu** (K-050'nin canlıda ilk gerçek doğrulaması) — kaydırma
testinin güvenilir sonuç vermediği ve nasıl daha iyi kayıt yapılabileceği
anlatıldı. Uydurma bir öneri sunulmadı; bu doğru/beklenen davranış.

Bu, benim (yapay zekâ asistanı) doğrulayamadığım son noktayı da kapatıyor:
uygulama artık gerçek bir kullanıcıda, gerçek bir cihazda, gerçek internet
üzerinden uçtan uca çalıştığı kanıtlanmış durumda.

**Performans notu:** Canlı backend'e sentetik bir ses dosyasıyla `curl` ile
yapılan doğrudan test, "uyanık" durumdaki backend'de bile analizin ~22
saniye sürdüğünü gösterdi (yerelde neredeyse anındaydı) — Render'ın
ücretsiz katmanının CPU'su zayıf. Frontend'de bir istemci tarafı zaman
aşımı (timeout) olmadığı için (`App.tsx` — `AbortController` yalnızca
bileşen kaldırılırsa iptal ediyor, süre bazlı değil) uygulama sessizce
başarısız olmuyor, ne kadar sürerse sürsün cevabı bekliyor.

### Sonraki adım

Aşama 8 hem kod hem gerçek canlı kullanım açısından tamamlandı. Kullanıcı
isterse `https://sestiny.vercel.app` adresini başkalarıyla paylaşıp daha
fazla gerçek kullanıcı testi toplayabilir. Bilinen davranış: Render'ın
ücretsiz katmanı birkaç dakika boşta kalınca "uyur", ilk istek bu yüzden
10-30 saniye + ~20 saniye analiz süresi toplayıp ~1 dakikaya kadar
sürebilir — bu beklenen bir durum, hata değil.

---

## Şarkı Havuzu Genişletmesi · 2026-08-06

Kullanıcı daha fazla yabancı ve Türkçe gerçek şarkı istedi.

### Yapılanlar

- `singingcarrots.com`'da 13 yeni gerçek şarkı araştırılıp doğrulandı (bkz.
  K-057): The Beatles, Whitney Houston, John Legend, Michael Jackson,
  Bruno Mars, Sam Smith, Coldplay, Billie Eilish, Guns N' Roses, Frank
  Sinatra, Louis Armstrong, BTS, Toto. Havuz 16 → **29 gerçek şarkıya**
  çıktı (+ 12 demo şarkı, toplam 41).
- **Türkçe şarkı için yine kaynak bulunamadı** — bu sefer daha kapsamlı
  arandı (sanatçı listesi taraması, 6 farklı Türk sanatçı için doğrudan
  deneme, akor/BPM siteleri gibi alternatif kaynaklar). Akor/BPM
  siteleri yalnızca müzikal tonu (key) veriyor — bu, şarkının gerçekten
  söylenen nota aralığı değil, o yüzden veri kaynağı olarak kullanılmadı
  (kullanılsaydı yanıltıcı olurdu). Uydurma bir Türkçe liste
  oluşturulmadı.

### Testler

| Test | Sonuç |
| --- | --- |
| Backend (pytest) | ✅ 55/55 (regresyon yok) |
| JSON doğrulama (ID çakışması, min<max, verified=true, kaynak URL'i) | ✅ |

### Doğrulanamayan / açık nokta

Türkçe gerçek şarkı verisi hâlâ yok. Güvenilir bir kaynak (ör. bir Türk
vokal koçunun/topluluğunun yayınladığı doğrulanabilir bir liste) bulunursa
kolayca eklenebilir — veri modeli zaten `language` alanını destekliyor.

### Sonraki adım

Kullanıcı isterse belirli Türkçe şarkı/sanatçı önerip kaynak paylaşabilir
(ör. bir vokal koçunun videosu/yazısı) — o zaman doğrudan eklenebilir.
Aksi hâlde bu boşluk açık kalıyor.

---

## Şarkı Havuzu — Büyük Genişletme · 2026-08-06

Kullanıcı "1000+ şarkı" hedefiyle telifli ses dosyalarını indirip
Sestiny'nin kendi motoruyla analiz etmeyi önerdi. Bu reddedildi (bkz.
K-058): hem yasal indirme yolu yok hem de analiz motoru tam prodüksiyonlu
kayıtlar için değil, tek/temiz ses için tasarlandı — o yolla üretilecek
veri hem izinsiz hem güvenilmez olurdu. Bunun yerine mevcut kanıtlanmış
yöntemle (singingcarrots.com, gerçek kaynak URL'i) büyük bir tarama
yapıldı.

### Yapılanlar

- 32 popüler şarkı denendi, 27'si başarıyla doğrulandı: Queen, Elton
  John, George Michael, Whitney Houston, Sia, Katy Perry, Rihanna,
  Beyoncé, Christina Aguilera, Taylor Swift, Shawn Mendes, Imagine
  Dragons, Maroon 5, Oasis, Nirvana, U2, Bon Jovi, Fleetwood Mac, ABBA,
  The Beatles (Hey Jude), David Bowie, Eric Clapton, Amy Winehouse,
  Alicia Keys, Coldplay (Yellow), Snow Patrol, Lewis Capaldi.
- Gerçek şarkı havuzu **29 → 56'ya** çıktı (demo 12 ile birlikte toplam
  68 şarkılık öneri havuzu).
- `singingcarrots.com`'un "aralığa göre listeleme" sayfaları da denendi
  ama sonuçlar çoğunlukla az tanınan ilahi/kilise müziğiydi — kullanıcının
  istediği "yüksek popülerlik" kriterine uymadığı için kullanılmadı,
  yalnızca tek tek doğrulanan tanınmış hitler eklendi.
- Türkçe şarkı durumu değişmedi — hâlâ kaynak yok (bkz. yukarıdaki kayıt).

### Testler

| Test | Sonuç |
| --- | --- |
| Backend (pytest) | ✅ 55/55 (regresyon yok) |
| JSON doğrulama (56 şarkı, ID çakışması yok, min<max, kaynak URL'i var) | ✅ |

### Sonraki adım

Bu değişiklik commit'lenip push edilecek, Render otomatik yeniden build
edecek. Kullanıcı isterse canlı sitede yeni şarkıların göründüğünü
doğrulayabilir. "1000+" hedefine ulaşmak için bu tarzda birden fazla
oturum daha gerekecek — bugünkü tur, yöntemin ölçeklenebilir olduğunu
gösterdi (32 denemede %84 başarı oranı).

---

## Türkçe Şarkı Havuzu — SymbTr Aktarımı · 2026-08-07

Kullanıcı Türkçe şarkı istedi ve "1000+" hedefi koydu. Türkçe için hiçbir
vokal aralığı veritabanı bulunamamıştı (iki ayrı oturumda arandı). Bu
oturumda çözüm bulundu ve uygulandı.

### Aranan ve elenen kaynaklar

| Kaynak | Sonuç |
| --- | --- |
| singingcarrots.com | Türkçe sıfır (üçüncü kez doğrulandı) |
| notanehri, kolaynota | Oktav bilgisi yok, bağlama için kaydırmalı — kullanılamaz |
| TRT Nota Arşivi | Login gerektiriyor, erişilemiyor |
| notaarsivleri.com | Açık ve büyük, ama notalar **taranmış JPEG** (PDF içinde) — göz kararı okuma gerektirir, güvenilmez |
| MuseScore | 403, otomatik erişim engelli |
| turkcemidi.com | Ücretli (179₺/şarkı) |
| Türkçe MIDI arşivleri | Bulunanlar ölü sunucular |
| **SymbTr (MTG/UPF)** | ✅ **Çözüm** |

Kullanıcının önerdiği "telifli ses dosyalarını indirip analiz et" yolu
K-058'de reddedilmişti; bu oturumda da aynı konumda kalındı.

### SymbTr aktarımı

[github.com/MTG/SymbTr](https://github.com/MTG/SymbTr) — Barcelona Universitat
Pompeu Fabra'nın Türk makam müziği veri seti: 2200 eser, MIDI + MusicXML +
txt, CC BY-NC-SA 4.0. Kullanıcı projenin ücretsiz kalacağını teyit etti,
NonCommercial kısıtı sorun değil.

`backend/scripts/import_symbtr.py` yazıldı (uygulamanın çalışma zamanının
parçası değil, tek seferlik veri hazırlama aracı):
- Dinî formlar elendi (kullanıcı isteği: "ilahi olmasın")
- Enstrümantal eserler elendi — form adına güvenmek yerine txt'deki söz
  sütununun doluluğuna bakılarak (içerik okunmadan, yalnızca sayılarak)
- `mido` ile min/max nota çıkarıldı
- Başlık ve besteci MusicXML'den okundu (dosya adları Türkçe karakter
  kaybediyor, bkz. K-063)
- **Sonuç: 1586 sözlü, dindışı Türkçe eser** — 841 şarkı, 281 türkü,
  120 küpe, semai/beste/fantezi ve diğerleri

### Çözülen üç gerçek sorun

1. **Mutlak perde sorunu (K-060):** Ham aralıklar medyan G4–C6 çıktı —
   makam müziğinde perde seviyesini icracı seçtiği için notasyon bir
   referans. Sabit bir düzeltme uydurmak yerine eserler "serbest transpoze
   edilebilir" olarak modellendi.
2. **Çeşitlilik çöküşü (K-061):** 1586 eser tüm önerileri süpürüyordu.
   Dil (6) ve sanatçı (2) kotası eklendi.
3. **Demo şarkılar (K-062):** Uydurma "Demo Şarkı" kayıtları üst sıraları
   işgal ediyor ve Türkçe kotasını dolduruyordu — en düşük katmana indirildi.

### Testler

| Test | Sonuç |
| --- | --- |
| Backend (pytest) | ✅ **64/64** (55 mevcut + 9 yeni: güven ağırlığı, serbest transpoze, çeşitlilik kotası, SymbTr atfı) |
| Frontend (Vitest) | ✅ **35/35** (1 yeni: serbest transpoze eserde sayı yerine açıklama) |
| Tip kontrolü, lint | ✅ temiz |

### Uçtan uca doğrulama

Yerel sunucuya sentetik bir kayıtla (G2–E4 kaydırma) istek atıldı:
tahmini rahat bölge A2–D#4 çıktı, öneriler **6 yabancı + 4 Türkçe**
karışımı geldi, Türkçe eserlerde sayısal yarı ton yerine "serbest perde"
ifadesi göründü. Demo şarkı hiç çıkmadı.

### Durum: havuz 68 → 1654 şarkı

| Grup | Adet |
| --- | --- |
| Türkçe (SymbTr) | 1586 |
| Yabancı (singingcarrots) | 56 |
| Demo (son çare) | 12 |

**"1000+" hedefi tutmuş oldu**, ama içeriğin dürüst tarifi şu: Türkçe
tarafı Türk sanat müziği ve türkü repertuvarı — **modern Türkçe pop yok**
(Tarkan, Ceylan, Aleyna Tilki gibi). O boşluk için sıfır-katılımlı bir
kaynak bulunamadı; gerçekçi yol MuseScore/kulak yoluyla 50-150 şarkılık
kürasyon.

### Sonraki adım

Modern Türkçe pop kürasyonu ve yabancı havuzun tür listesi sayfalarıyla
büyütülmesi (bir önceki kayıtta anlatılan yöntem) hâlâ açık işler.

---

## Song Ingestion Lab — Faz 0 (iskelet) · 2026-08-07

Şarkı verisi darboğazını kalıcı çözmek için, ses kaydından offline vokal
aralığı çıkaran ayrı bir geliştirici aracı planlandı ve iskeleti kuruldu.
Önce ayrıntılı teknik plan hazırlanıp kullanıcı onayı alındı (2025 ses-ML
tooling araştırması dahil). Karar detayları: K-064 – K-067.

### Yapılanlar (bu commit, ağır ML KURULMADAN)

**Production (küçük, geriye uyumlu):**
- `Song`'a `tessitura_low/high_midi` + `vocal_mode` (nullable/varsayılan) —
  eski 3 JSON dosyası hiç değişmeden yükleniyor.
- `score_song` tessitura'yı önceler; full range yalnızca tavanlı (15 puan)
  hafif ikincil ceza (K-064). Tessitura yoksa davranış eskiyle birebir aynı.

**Lab iskeleti (`tools/song_ingestion/`, ayrı venv/bağımlılık):**
- `models.py` (`LabSong` zengin model), `notes.py`, `catalog.py` (SQLite:
  resume, review durumu, migrate), `decode.py` (PyAV, lazy), `batch.py`
  (hata yalıtımı + content-hash resume), `export.py` (onaylı→production JSON).
- `ingest/` aşama modülleri (separate/pitch/segment/range/confidence/pipeline)
  — arayüz + sözleşme hazır, gövdeler Faz 1'de dolacak; ağır importlar lazy.
- `requirements.txt` (ayrı; Faz 1'de kurulacak, backend'e girmez).

### Testler

| Test | Sonuç |
| --- | --- |
| Backend (pytest) | ✅ **68/68** (64 + 4 yeni tessitura testi) |
| Lab (pytest, stdlib) | ✅ **16/16** (katalog CRUD/resume, batch hata yalıtımı+resume, export; export JSON'u production Song ile yükleniyor) |

### Doğrulanamayan / sonraki

Ağır ML (ayrıştırma + pitch modelleri) henüz kurulmadı/denenmedi — **Faz 1**.
Onu takiben Faz 2 (30-50 yabancı şarkıyla calibration, doğruluk eşiği), Faz 3
(batch + review arayüzü), Faz 4 (Türkçe pilot), Faz 5 (ölçekleme). Her faz
sonunda durulup kullanıcı onayı beklenecek. Sınır değişmedi: araç ses dosyası
edinmez, kullanıcı kendi dosyalarını verir; export insan onayına bağlı.

---

## Song Ingestion Lab — Faz 1 / Adım 1-2: Direct RMVPE motoru · 2026-08-07

Kullanıcı Faz 1'i "Pitch Pipeline Benchmark" olarak yeniden şekillendirdi:
vokal ayrıştırmayı ölçmeden zorunlu kılmamak, önce Direct RMVPE'yi kurup
çalıştırmak (bkz. K-068). Bu adımda yalnızca Direct RMVPE analiz motoru
tamamlandı; separation/MLX/batch/UI/export'a girilmedi.

### Donanım (tespit edildi, kurulumdan önce)

Apple **M1 Ultra** (arm64), **128 GB RAM**, macOS 15.7.2, Python 3.12.13.
→ MLX-native yol uygulanabilir, torch'a mecbur değiliz; RAM hiç sorun değil.

### Kurulan (yalnızca, kullanıcı onaylı)

Ayrı lab venv'ine `rmvpe-onnx==0.2.3` — **torch YOK**. onnxruntime (arm64 +
CoreML), librosa, scipy, numpy, huggingface-hub bağımlılık olarak geldi.
Model rmvpe.onnx (362 MB) ilk çalışmada indi.

### Yazılan motor (Direct RMVPE)

`config.py` (merkezî eşikler), `ingest/pitch.py` (RMVPE lazy), `note_segments.py`
(filtre + segmentasyon), `range.py` (full range + tessitura), `confidence.py`
(ölçüm-tabanlı), `engine.py` (orchestrator + AnalysisResult + debug JSON).
Ayrıntılı yöntem: `docs/ANALYSIS_THRESHOLDS.md`. Kararlar: K-069.

### Testler

| Test | Sonuç |
| --- | --- |
| Production backend | ✅ 68/68 |
| Lab (backend venv) | ✅ **25 geçti** + 1 atlandı (RMVPE entegrasyonu importorskip) |
| Sentetik motor (A-F) | ✅ 9/9 — sabit A3, A3-C4-E4, spike reddi, kısa-yüksek-nota reddi, glide (parçalanmıyor), sessizlik→needs_review, ad-lib tessitura'yı genişletmiyor, debug şekli |
| Gerçek RMVPE smoke (lab venv) | ✅ 220 Hz → A3, güven 0.935; soğuk ~5.9 sn, sıcak inference ~0.04 sn |

### Bilinen sınırlamalar / sonraki

- Henüz gerçek şarkı denenmedi (yalnızca sentetik ton). Eşikler MVP heuristiği;
  gerçek şarkı calibration'ında (sonraki faz) ayarlanacak.
- Vokal ayrıştırma (Pipeline B) kurulmadı; Direct vs Separated benchmark'ı
  gerçek şarkı gerektiriyor. Sıra: kullanıcı gerçek şarkı verince A vs B.
- Production backend hâlâ hiçbir ağır ML bağımlılığı almadı (Render hafif).

Bu noktada durulup gerçek şarkı testi için kullanıcı onayı bekleniyor.
