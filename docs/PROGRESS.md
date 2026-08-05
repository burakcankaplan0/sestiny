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
