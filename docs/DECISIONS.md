# Teknik Kararlar

Bu dosyada alınan her önemli teknik karar, gerekçesiyle birlikte kısaca kaydedilir.
En yeni karar en üstte değil, kronolojik sırayla en altta eklenir.

---

## Aşama 0 — 2026-08-04

### K-001: Proje kökü olarak mevcut `Sestiny/` klasörü kullanılıyor
Orijinal planda `SestinyClean/` adlı bir klasör geçiyordu. Mevcut çalışma klasörü
(`~/Desktop/Sestiny`) tamamen boştu ve zaten proje için ayrılmıştı.
İçine bir kat daha klasör açmak gereksiz derinlik yaratırdı.
**Karar:** Proje kökü `~/Desktop/Sestiny`. `frontend/`, `backend/`, `docs/` doğrudan burada.

### K-002: Frontend'de yönlendirme başta React Router ile değil, basit state ile yapılacak
Uygulama akışı doğrusal bir sihirbaz (karşılama → mikrofon → 3 test → analiz → sonuç).
Bu akış için URL tabanlı yönlendirme ek bir bağımlılık ve karmaşıklık demek.
**Karar:** Adımlar tek bir `useState` ile yönetilecek. Paylaşılabilir sonuç bağlantısı
gibi gerçek bir ihtiyaç doğarsa React Router sonradan eklenir.

### K-003: Global state kütüphanesi kullanılmayacak
Paylaşılan durum sadece "3 kayıt + analiz sonucu". Bu, App seviyesinde bir state ve
prop geçişiyle rahatça yönetilir.
**Karar:** Redux/MobX/Zustand yok. Prop drilling sorun olursa React Context yeterli.

### K-004: Kayıtlar tek bir istekte gönderilecek
Üç kaydın ayrı ayrı gönderilmesi yerine tek `POST /api/v1/analyze-session` isteğinde
üç dosya birden gönderilecek. Böylece sunucu tarafında oturum durumu tutmak gerekmez —
veritabanı olmadığı için bu önemli bir sadeleştirme.
**Karar:** Tek istek, üç multipart alanı (`speech`, `sustained_vowel`, `glide`).

### K-005: Python sürümü 3.12 hedefleniyor
Sistemde yalnızca Xcode ile gelen Python 3.9.6 var; librosa'nın bağımlılığı olan
numba 3.9'da eski sürümlere zorlar ve ilerideki sorunların kaynağı olur.
Python 3.13 en yeni olsa da librosa/numba/numpy üçlüsünün en çok test edilmiş
kombinasyonu 3.12'dir.
**Karar:** Homebrew ile `python@3.12` kurulacak (kullanıcı onayı bekleniyor).
Sistem Python'una dokunulmayacak; backend kendi `.venv` klasöründe izole çalışacak.

### K-006: Node.js 20 LTS hedefleniyor
Vite 5+ için Node 18+ gerekir. LTS sürüm en az sürprizi verir.
**Karar:** Homebrew ile `node` kurulacak (kullanıcı onayı bekleniyor).
**Güncelleme (Aşama 1):** Homebrew'un `node` formülü güncel sürümü (26.6.0) kurdu.
Vite 8 derlemesi, testler ve tip kontrolü bu sürümde sorunsuz çalıştığı için ayrıca
LTS'e düşürülmedi. İleride bir araç uyumsuzluk çıkarırsa `node@22`'ye geçilecek.

### K-007: Ses format dönüştürme aracı Aşama 3'te kesinleşecek
Tarayıcılar WebM/Opus veya MP4/AAC üretir; `soundfile` (libsndfile) bunları okuyamaz.
İki seçenek var:
1. **FFmpeg** — Homebrew ile sistem geneline kurulur, standart ve güvenilir.
2. **PyAV** — pip paketi, FFmpeg kütüphanelerini kendi içinde taşır, sadece `.venv`
   içine kurulur, sistemde hiçbir değişiklik yapmaz.
**Karar:** Tercih edilen seçenek PyAV'dir (sistem geneline kurulum gerektirmez).
Aşama 3'te gerçek tarayıcı kayıtlarıyla denenip kesinleştirilecek; PyAV yetersiz
kalırsa kullanıcıdan FFmpeg kurulumu için izin istenecek.

### K-008: Ses analizi için 22.050 Hz mono kullanılacak
İnsan sesi temel frekansı en fazla ~1100 Hz civarındadır; 22.05 kHz örnekleme
(Nyquist ~11 kHz) pitch analizi için fazlasıyla yeterlidir ve `librosa.pyin`
çok daha hızlı çalışır.
**Karar:** Tüm analiz sesi mono, 22.050 Hz, float32'ye normalize edilir.

### K-009: Kayıt kalitesi kontrolü, normalizasyondan **önce** yapılacak
Ses seviyesi normalize edildikten sonra ölçüm yapılırsa, çok sessiz veya bozuk bir
kayıt yapay olarak iyi görünür ve kullanıcı hatalı sonuca güvenir.
**Karar:** RMS, peak, clipping ve sessizlik ölçümleri ham (dönüştürülmüş ama
normalize edilmemiş) sinyal üzerinde yapılır.

### K-010: Sonuçta klasik ses türü sınıflandırması yapılmayacak
Tek bir glide kaydından bariton/tenor/soprano gibi bir sınıflandırma yapmak,
verinin taşıyabileceğinden fazla iddia demektir ve kullanıcıyı yanıltır.
**Karar:** Profil, "orta-düşük merkezli ses profili" gibi merkez bölge tanımı ve
"orta genişlikte gözlemlenen aralık" gibi ikinci bir açıklamayla sunulur.
Cinsiyet tahmini yapılmaz.

### K-011: Ham ses kayıtları kalıcı saklanmayacak
Ses kaydı kişisel veridir. Saklamanın ilk sürümde hiçbir ürün faydası yok,
buna karşılık gizlilik riski var.
**Karar:** Geçici dosyalar güvenli rastgele isimlerle oluşturulur ve analiz bitince
(hata durumunda da) `finally` bloğunda silinir. Ses içeriği loglanmaz.
`.gitignore` tüm yaygın ses formatlarını dışlar.

---

## Aşama 1 — 2026-08-04

### K-012: Backend bağımlılıkları aşama aşama eklenecek
`requirements.txt` şu an yalnızca FastAPI, Uvicorn, Pydantic ve test araçlarını içeriyor.
librosa/NumPy/SciPy/SoundFile ağır paketler; henüz tek satır kod onları kullanmıyor.
"Kullanılmayan bağımlılık bırakma" kuralı gereği erken eklenmiyorlar.
**Karar:** Ses kütüphaneleri Aşama 3/4'te, gerçekten kullanıldıkları anda eklenecek.

### K-013: Frontend'de TypeScript `strict` modu açıldı
Vite şablonu `strict` bayrağını tanımlamadan geldi. Bu hâliyle `any` sızıntıları ve
`null` kontrolü eksikleri sessizce geçerdi — CLAUDE.md'deki tip güvenliği kuralına aykırı.
**Karar:** `tsconfig.app.json` içine `strict` ve `noImplicitOverride` eklendi.

### K-014: Test aracı olarak Vitest 4 kullanılıyor
Vitest 3, kendi içinde eski (rollup tabanlı) bir Vite kopyası taşıyor ve projedeki
Vite 8 (rolldown) ile tip çakışması üretti — `tsc -b` hata verdi.
**Karar:** Vitest 4'e geçildi; kendi Vite kopyasını taşımıyor, tip kontrolü temiz geçiyor.

### K-015: Hatalar kullanıcıya tek bir sarmalayıcıdan geçerek gösteriliyor
Backend isteklerinin tamamı `src/api/client.ts` üzerinden yapılıyor. Bu katman
HTTP kodunu, ağ hatasını ve JSON ayrıştırma hatasını yakalayıp önceden yazılmış
Türkçe mesaja çeviriyor; ham detay yalnızca `ApiError.detail` alanında kalıyor.
**Neden:** Teknik hata metinlerinin arayüze sızması tek tek `catch` bloklarına
bırakılırsa er geç biri unutulur.
**Karar:** UI bileşenleri asla ham hata nesnesi göstermez. Testler bunu doğruluyor
(HTTP 500 ve "Failed to fetch" metinlerinin ekranda **olmadığı** kontrol ediliyor).

### K-016: Kullanıcı metinleri `src/texts.ts` içinde toplandı
Ürünün en kritik kuralı, "kesin teşhis" iması taşıyan cümle kurmamak. Metinler
bileşenlerin içine dağılırsa bunu gözden geçirmek imkânsızlaşır.
**Karar:** Tüm kullanıcı metinleri tek dosyada. Bileşenler metin string'i yazmaz.

### K-017: Bağlantı durumu yalnızca renkle anlatılmıyor
Yeşil/kırmızı kart, renk körlüğü olan veya ekran okuyucu kullanan biri için bilgi taşımaz.
**Karar:** Kartta ayrıca "Bağlı / Bağlanamadı / Kontrol ediliyor" metin etiketi var ve
kart `role="status" aria-live="polite"` ile duyuruluyor.
