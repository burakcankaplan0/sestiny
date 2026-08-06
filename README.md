# Sestiny

Sestiny, kullanıcıdan üç kısa ses kaydı alarak **tahmini bir ses profili** çıkaran ve
bu profile uygun şarkılar önermeyi hedefleyen, web tabanlı bir uygulamadır.

> **Önemli:** Sestiny bir sağlık uygulaması, tıbbi analiz aracı veya profesyonel vokal
> teşhis sistemi **değildir**. Ürettiği sonuçlar yaklaşık değerlendirmelerdir; mikrofon
> kalitesi, ortam gürültüsü, kayıt tekniği ve o anki ses durumundan etkilenir.

## Durum

✅ **Aşama 7 (Kalite, test, dokümantasyon) tamamlandı**, ardından gerçek şarkı
verisi eklendi. Uçtan uca akış çalışıyor: kayıt yap → analiz et → tahmini ses
profilini ve sana uygun şarkı önerilerini gör — artık 12 demo kaydın yanında
16 gerçek, kaynaklı şarkı da (`singingcarrots.com`'dan) öneriliyor.

🚧 **Aşama 8 (Yayına hazırlık) kullanıcı onayıyla başladı** (bkz.
`docs/DECISIONS.md` K-051). Kod tabanı gerçek bir internet dağıtımına
(Render + Vercel, ücretsiz katman) hazır hâlde: prod-güvenli varsayılanlar,
hız sınırlama, deploy manifestleri — bkz. aşağıdaki "Yayına alma" bölümü.
**Gerçek canlı dağıtım henüz yapılmadı** — hesap açma/repo bağlama gibi
adımlar kullanıcı eylemi gerektiriyor, bu yüzden "canlıda çalışıyor" iddia
edilmiyor (bkz. `docs/PROGRESS.md`).

## Nasıl çalışır?

1. Kullanıcı kısa bir cümleyi doğal konuşma sesiyle okur (**konuşma testi**).
2. Rahat bir tonda uzun bir "Aaaa" sesi tutar (**uzun ünlü testi**).
3. "Aaaa" diyerek sesini kalından inceye kaydırır (**glide testi**).
4. Backend kayıtları analiz eder: konuşma perdesi, ses kararlılığı, gözlemlenen nota aralığı.
5. Sonuç ekranında tahmini ses profili ve şarkı önerileri gösterilir.

## Teknoloji

| Katman | Teknoloji |
| --- | --- |
| Frontend | React, TypeScript, Vite, sade modüler CSS |
| Backend | Python 3.11+, FastAPI, Uvicorn |
| Ses format dönüştürme | PyAV (ffmpeg kütüphanelerini pip paketinin içinde taşır — sisteme ayrıca FFmpeg kurulmadı, bkz. `docs/DECISIONS.md` K-007/K-023) |
| Ses analizi | librosa (`pyin`), NumPy, SciPy |
| Testler | pytest (backend), Vitest + Testing Library (frontend) |

Kullanıcı hesabı, veritabanı, ödeme sistemi ve harici yapay zekâ API'si yoktur —
bu, uygulama yayına alınsa bile değişmez. Uygulama varsayılan olarak tamamen
lokal çalışır; kullanıcının ayrıca ve açıkça onayıyla (Aşama 8) ücretsiz
katman PaaS üzerinde de yayınlanabilir (bkz. "Yayına alma" bölümü).

## Gereksinimler

| Araç | Gereken sürüm | Doğrulandığı sürüm |
| --- | --- | --- |
| Node.js | 20 veya üzeri | 26.6.0 |
| npm | Node ile gelir | 11.18.0 |
| Python | 3.11 veya üzeri | 3.12.13 |
| Git | 2.x | 2.50.1 |

FFmpeg sisteme ayrıca kurulmaz — PyAV bunu kendi içinde taşır.

## Kurulum

Bir kereye mahsus, proje kökünde:

```bash
python3.12 -m venv backend/.venv && backend/.venv/bin/pip install -r backend/requirements.txt && npm --prefix frontend install
```

İsteğe bağlı — varsayılan ayarları değiştirmek istersen:

```bash
cp backend/.env.example backend/.env && cp frontend/.env.example frontend/.env
```

## Çalıştırma

İki ayrı terminal gerekir.

**Terminal 1 — backend** (http://127.0.0.1:8000):

```bash
cd backend && .venv/bin/uvicorn app.main:app --reload
```

**Terminal 2 — frontend** (http://localhost:5173):

```bash
npm --prefix frontend run dev
```

Tarayıcıda http://localhost:5173 adresini aç. Bağlantı kartında
"Backend bağlantısı başarılı" yazmalı.

İnteraktif API dokümanı: http://127.0.0.1:8000/docs

## Testler

**Backend:**

```bash
cd backend && .venv/bin/python -m pytest
```

**Frontend** (testler + tip kontrolü + lint):

```bash
npm --prefix frontend test && npm --prefix frontend run typecheck && npm --prefix frontend run lint
```

## Yayına alma (deploy)

Bu bölüm, uygulamayı gerçek bir internet adresinde (kendi bilgisayarın kapalıyken
de erişilebilir şekilde) yayınlamak isteyenler için. **Bu adımları benim (yapay
zekâ asistanının) yapması mümkün değil** — hesap açmak ve bir hesaba GitHub reposu
bağlamak kullanıcı eylemi gerektiriyor. Kod tarafı hazır; aşağıdaki adımlar senin
kendi tarayıcında, kendi hesaplarınla yapılır.

Seçilen hosting: **Vercel** (frontend) + **Render** (backend) — ikisi de ücretsiz
katmanda çalışır, HTTPS otomatik gelir. Sıra önemli: önce frontend'in adresini
almalısın, çünkü backend'in CORS ayarı o adrese ihtiyaç duyuyor.

1. **GitHub'a it.** Bu repo henüz bir GitHub reposuna bağlı değilse, önce oraya gönder
   (Vercel/Render ikisi de GitHub reposu üzerinden çalışır).
2. **Vercel'de frontend'i oluştur:** [vercel.com](https://vercel.com) → "Add New Project" →
   bu repoyu seç → **Root Directory: `frontend`** → Framework Preset: Vite (otomatik
   algılanır) → Environment Variable ekle: `VITE_API_BASE_URL` = `http://127.0.0.1:8000`
   (şimdilik geçici bir değer, adım 4'te güncellenecek) → Deploy.
3. Deploy bitince Vercel'in verdiği gerçek adresi not al (ör. `https://sestiny-xxxx.vercel.app`).
4. **Render'da backend'i oluştur:** [render.com](https://render.com) → "New Web Service" →
   bu repoyu seç. Render `render.yaml` dosyasını bulup bir Blueprint önerebilir — kabul et;
   önermezse veya alanlar tanıdık gelmezse şu değerleri elle gir (Render'ın panel arayüzü
   zamanla değişebilir, bu yüzden bu liste asıl referans):
   - **Root Directory:** `backend`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables:**
     - `SESTINY_DEBUG` = `false`
     - `SESTINY_ALLOWED_ORIGINS` = adım 3'te aldığın gerçek Vercel adresi (`https://sestiny-xxxx.vercel.app`)
     - `SESTINY_MAX_UPLOAD_BYTES` = `10485760`
     - `PYTHON_VERSION` = `3.12.13`
   - Plan: Free
5. Deploy bitince Render'ın verdiği gerçek adresi not al (ör. `https://sestiny-backend-xxxx.onrender.com`).
6. **Vercel'e dön**, proje ayarlarından `VITE_API_BASE_URL`'i adım 5'teki gerçek Render
   adresiyle güncelle ve **yeniden deploy et** — Vite bu değeri derleme sırasında koda
   gömüyor, yalnızca ortam değişkenini değiştirmek yetmez, yeniden build gerekir.
7. Vercel adresini bir tarayıcıda aç, uçtan uca dene (mikrofon izni, 3 test, analiz).

**Bilinmesi gerekenler:**
- Render'ın ücretsiz katmanı birkaç dakika boşta kalınca "uykuya dalar" — ilk istek
  10-30 saniye sürebilir, bu normal.
- `librosa`/`numpy`/`av` gibi native bağımlılıklar Render'ın ücretsiz katmanında build
  sırasında uzun sürebilir; build zaman aşımına uğrarsa Render'ın build loglarına bakılmalı.
- Bu adımların gerçek bir Render/Vercel hesabıyla uçtan uca çalıştığı benim tarafımdan
  **doğrulanamadı** — hesap açamadığım için (bkz. `docs/PROGRESS.md` Aşama 8 kaydı).
  Yerel olarak doğrulayabildiğim kısım: prod-benzeri ortam değişkenleriyle backend'in
  yerelde doğru çalıştığı, derlenmiş (production) frontend build'inin backend'e doğru
  bağlandığı ve hız sınırlamanın çalıştığı.

## Gizlilik

Ses kayıtların yalnızca bu analiz için işlenir. Kayıtlar kalıcı olarak
saklanmaz ve analiz tamamlandıktan sonra (başarılı ya da başarısız fark etmez)
geçici dosyalar silinir. Ses içeriği veya ham binary veri hiçbir log seviyesinde
yazılmaz — yalnızca oturum kimliği ve sonuç (kabul/ret) loglanır. Hata mesajlarında
dosya yolu veya teknik iz (traceback) gösterilmez. Kullanıcı hesabı ve veritabanı
yoktur. Uygulama varsayılan olarak tamamen kendi bilgisayarında çalışır; yukarıdaki
"Yayına alma" adımlarıyla kullanıcı kendi isteğiyle yayına alırsa, ses kaydı analiz
sırasında (HTTPS üzerinden) seçilen hosting sağlayıcısının (Render) sunucusuna gider
— yine kalıcı saklanmadan, işlem bitince hemen silinerek.

## Bilinen sınırlamalar

- **Tek bir kaydırma testi gerçek profesyonel tessiturayı kesin belirleyemez.**
  Sonuçlar "tahmini" ve "gözlemlenen" dilinde sunulur, kesin teşhis değildir.
- Tarayıcı mikrofonları genelde otomatik kazanç/gürültü bastırma uygular; bu
  yüzden mutlak ses seviyesi ölçümleri (RMS, peak) cihazdan cihaza değişebilir.
- `librosa.pyin` bazen oktav hatası yapabilir (bir notayı bir oktav yukarı/aşağı
  algılama); kod bunu büyük ölçüde filtreler ama tamamen ortadan kaldırmaz.
- Stabilite skoru ve tahmini profil kategorileri (K-013, bölüm 13/4) **klinik
  veya bilimsel bir standarda dayanmaz** — deneyimsel başlangıç eşikleridir.
- Şarkı önerileri 12 demo kayıt ("Demo Şarkı 1", "Demo Şarkı 2"...) ve
  `singingcarrots.com` kaynaklı 16 gerçek şarkıdan (`verified: true`, her
  birinin kaynağı `source_note` alanında) oluşan küçük bir havuzdan geliyor —
  kapsamlı bir müzik kütüphanesi değil. **Türkçe gerçek şarkı yok**: kullanılan
  kaynakta Türkçe şarkı verisi bulunamadı, uydurma bir liste oluşturulmadı.
- Uygulama yalnızca güncel Chrome/Edge/Safari gibi `MediaRecorder` ve
  `getUserMedia` destekleyen tarayıcılarda çalışır; eski tarayıcılarda anlaşılır
  bir "desteklenmiyor" mesajı gösterilir ama kayıt yapılamaz.
- Backend tek bir işlemde (process) çalışır; aynı anda çok sayıda kullanıcının
  yoğun kullanımı için ölçeklenmemiştir (ilk sürüm kapsamı dışı).

## Manuel test kontrol listesi

Otomatik testler (55 backend + 34 frontend testi) her commit'te çalışır, ama bazı
şeyler yalnızca gerçek bir tarayıcı ve gerçek bir mikrofonla elle doğrulanabilir.
Önemli bir değişiklikten sonra şunları kontrol et:

- [ ] Karşılama ekranı açılıyor, backend bağlantısı "Bağlı" gösteriyor
- [ ] Backend kapalıyken sayfa açılırsa anlaşılır hata + "Tekrar dene" çalışıyor
- [ ] Mikrofon izni istendiğinde tarayıcı izin penceresi çıkıyor
- [ ] İzin reddedilirse anlaşılır Türkçe hata mesajı gösteriliyor
- [ ] İzin verilince ses seviyesi çubuğu konuşurken hareket ediyor
- [ ] Üç test de gerçek sesle kaydedilip dinlenebiliyor
- [ ] Bir kayıt silinip yeniden yapılabiliyor
- [ ] Minimum süreden kısa bir kayıtta "Sonraki" pasif kalıyor
- [ ] Kayıt varken sayfa yenilenirse tarayıcı uyarısı çıkıyor
- [ ] İnceleme ekranında üçü de tamamlanmadan "Analiz et" pasif
- [ ] "Analiz et" gerçek backend'e istek atıyor, sonuç ekranı doğru veri gösteriyor
- [ ] Çok kısa/sessiz bir kayıtla analiz denendiğinde ret nedeni açıkça anlatılıyor
- [ ] Şarkı önerilerinde zorluk filtresi doğru filtreliyor
- [ ] "Testi yeniden yap" tüm kayıtları temizleyip baştan başlatıyor
- [ ] Mobil genişlikte (375px) hiçbir ekranda yatay taşma yok
- [ ] Yalnızca klavye ile (Tab/Enter) tüm akış tamamlanabiliyor
- [ ] Tarayıcı konsolunda hata/uyarı yok

## Belgeler

- `CLAUDE.md` — projenin bağlayıcı geliştirme kuralları
- `docs/PROJECT_PLAN.md` — mimari ve aşama aşama geliştirme planı
- `docs/DECISIONS.md` — alınan teknik kararlar ve gerekçeleri
- `docs/PROGRESS.md` — aşama aşama ilerleme kaydı
