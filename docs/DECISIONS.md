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

---

## Aşama 2 — 2026-08-05

### K-018: Mikrofon akışı (MediaStream) tüm oturum boyunca tek sefer alınıyor
Her testte ayrı `getUserMedia` çağrısı yapmak, kullanıcıya üç kez izin sorusu
gösterebilir (tarayıcıya göre değişir) ve gereksiz karmaşıklık yaratır.
**Karar:** İzin, Mikrofon Kontrolü ekranında bir kez istenir; elde edilen
`MediaStream` App bileşeninde tutulur ve üç test ekranında da yeniden kullanılır.
Akış yalnızca uygulama kapanırken (unmount) durdurulur.

### K-019: Kayıt makinesi (useAudioRecorder) kendi sonucunu saklamıyor
Kayıt tamamlandığında hook, sonucu bir `onComplete` callback ile yukarı bildirip
kendi iç durumunu hemen `idle`'a döndürüyor; "tamamlanan kayıt" tek doğruluk
kaynağı olarak App'teki `recordings` state'inde tutuluyor.
**Neden:** Aynı veriyi hem hook içinde hem App'te tutmak senkronizasyon hatasına
açık olurdu (örn. sil/yeniden kaydet sırasında iki kaynağın çelişmesi).

### K-020: Ses seviyesi göstergesi (mikrofon kontrolü ekranı) yalnızca görsel geri bildirimdir
Web Audio API (`AnalyserNode`) ile hesaplanan RMS değeri hiçbir yerde saklanmaz
veya analiz edilmez; yalnızca kullanıcıya "mikrofon çalışıyor" güvenini vermek
için bir çubuk olarak gösterilir. `AudioContext` desteklenmeyen bir tarayıcıda
özellik sessizce devre dışı kalır (seviye her zaman 0 döner), akışı bozmaz.

### K-021: Test süresi eşikleri (min/önerilen/maks) `testConfig.ts` içinde tek merkezde
CLAUDE.md'nin "ses analizi eşiklerini merkezi config'te tut" kuralı burada da
uygulandı: üç testin talimat metni ve süre sınırları `VOICE_TESTS` dizisinde,
bileşenlerin içine dağılmadan tutuluyor.

### K-022: "Sonraki" butonu yalnızca minimum süre karşılanınca aktifleşiyor
Kayıt kalitesi kontrolü (RMS, clipping, sessizlik) backend'in işi (Aşama 3);
ama süre kontrolü tamamen istemci tarafında, anında yapılabilecek bir kontrol.
**Karar:** İstemci yalnızca "kayıt en az min saniye mi" kontrolü yapar; daha
gelişmiş kalite kontrolleri backend'e bırakılır, burada tekrarlanmaz.

---

## Aşama 3 — 2026-08-05

### K-023: Ses format dönüştürme için FFmpeg değil PyAV kullanılıyor
K-007'de iki seçenek bırakılmıştı: sistem geneline FFmpeg kurmak veya PyAV
(pip paketi, ffmpeg kütüphanelerini kendi içinde taşır) kullanmak.
Gerçek bir tarayıcı kaydına en yakın senaryo olan WebM/Opus dosyasıyla PyAV
denendi: kodlama + çözme + 22.050 Hz'e yeniden örnekleme sorunsuz çalıştı
(bkz. test: `test_unsupported_format_is_rejected` ve canlı sunucuda WebM/Opus ile
yapılan manuel HTTP testi).
**Karar:** PyAV kullanılıyor. Sisteme FFmpeg kurulmadı, kurulmayacak — bu,
"sistem geneline kurulum" izni gerektirmeyen daha basit çözüm.

### K-024: Dosya formatı, MIME/uzantıya değil gerçek çözümlemeye göre doğrulanıyor
CLAUDE.md açıkça "MIME türü tek başına güvenilir kabul edilmemeli" ve "dosya
uzantısına tek başına güvenilmemeli" diyor.
**Karar:** Ayrıca bir magic-byte kontrolü yazmak yerine, dosya doğrudan PyAV ile
açılmaya çalışılıyor; açılamıyorsa veya ses akışı yoksa reddediliyor. Bu, sahte
uzantılı veya bozuk dosyaları da gerçek şekilde eler — sahte bir "İyi" sonuca
göre değil, gerçek çözümlemeye göre karar verilir.

### K-025: Kalite kontrolü tek bir 0-100 skora ve kabul/ret kararına indirgeniyor
CLAUDE.md'nin örnek JSON şemasında session genelinde tek bir `quality` nesnesi
var; ama Aşama 3'te henüz pitch analizi yok, dolayısıyla "profile" veya
"recommendations" gibi sonraki aşamalara ait alanları şimdiden boş/sahte
doldurmak "yarım bırakılmış kod" olurdu.
**Karar:** Şu an her test kaydı için ayrı bir `FileQualityReport` (accepted,
overall_score, label, warnings, duration_seconds) döndürülüyor. Oturum geneli
tek bir `quality` özeti, gerçek pitch/profil verisi ortaya çıkınca Aşama 4/5'te
`profile_builder.py` ile eklenecek — CLAUDE.md'deki tam şema o zaman tamamlanmış olacak.

### K-026: Uyarı mesajları CLAUDE.md'deki örnek cümlelerle birebir aynı
Bölüm 12'de sade Türkçe örnek uyarı cümleleri veriliyor ("Kayıt çok kısa
görünüyor.", "Ses zaman zaman bozulmuş veya kesilmiş görünüyor." vb.).
**Karar:** Kod bu cümleleri aynen kullanıyor; yeni/farklı ifadeler icat
edilmedi. Testler de bu cümlelerin doğru koşulda çıktığını doğruluyor.

### K-027: Aşırı büyük dosya HTTP 413 ile, kalite sorunları ise 200 + `rejected` ile bildiriliyor
İkisi farklı türde durumlar: aşırı büyük dosya bir güvenlik/kaynak koruma
konusu (saldırı senaryosu da olabilir), kalite sorunu ise geçerli bir kaydın
sonuçlarının yetersiz çıkması (normal kullanıcı senaryosu).
**Karar:** Boyut sınırı aşımı `HTTPException(413)` ile sert biçimde kesiliyor
(dosya hiç işlenmeden). Format/süre/ses seviyesi gibi kalite sorunları ise HTTP
200 ile, `status: "rejected"` ve testin kendi `warnings` listesiyle
bildiriliyor — böylece tek bir response şekli her durumda kullanılabiliyor.

---

## Aşama 4 — 2026-08-05

### K-028: SoundFile eklenmedi; PyAV + librosa.pyin doğrudan numpy dizisi üzerinde çalışıyor
CLAUDE.md'nin teknik yığınında SoundFile de sayılıyor, ancak SoundFile
(libsndfile) tarayıcının ürettiği WebM/Opus, MP4/AAC gibi formatları çözemiyor
— bu yüzden Aşama 3'te zaten PyAV'e geçildi (K-023). librosa'nın kendi
`librosa.load()` fonksiyonu dosya okurken arka planda soundfile/audioread
kullanır, ama biz dosyayı zaten Aşama 3'te PyAV ile numpy dizisine çevirmiş
durumdayız — `librosa.pyin()` bu diziyi doğrudan kabul ediyor.
**Karar:** SoundFile hiç eklenmedi; gereksiz/kullanılmayan bağımlılık
olurdu. `requirements.txt`'de bu sapmanın nedeni not edildi.

### K-029: Oktav hatası temizliği yalnızca "aynı sesli bölüm içindeki" sıçramalara uygulanıyor
İlk tasarımda ardışık güvenilir frame'ler arasındaki her büyük sıçrama
elenecekti; ama konuşma testinde iki ayrı hece arasında (arada sessiz boşluk
varken) perdenin gerçekten büyük değişmesi normaldir — bunu "oktav hatası"
sanıp silmek gerçek veriyi kaybettirir.
**Karar:** Yalnızca zaman olarak birbirine yakın (aynı kesintisiz sesli bölüm
içindeki, `hop_length`'in ~1.5 katından yakın) frame'ler arasındaki
MAX_SEMITONE_JUMP (6 yarı ton) üstü sıçramalar elenir; aralarında boşluk olan
frame'ler karşılaştırılmaz.

### K-030: "confidence" alanı, güvenilir şekilde takip edilen frame oranı olarak tanımlandı
CLAUDE.md her analiz sonucunda bir güven skoru istiyor ama tam formülünü
vermiyor. İstatistiksel bir güven aralığı hesaplamak (ör. bootstrap) bu
aşama için gereksiz karmaşıklık olurdu.
**Karar:** `confidence = temiz/güvenilir frame sayısı / toplam frame sayısı`,
0-1 arası. Kod içinde bunun istatistiksel bir güven aralığı olmadığı,
yalnızca "kaydın ne kadarında perde takip edilebildiği" anlamına geldiği
açıkça belirtiliyor.

### K-031: Kalitesi reddedilen bir kayıt için pitch analizi hiç çalıştırılmıyor
Süresi çok kısa, çok sessiz veya bozuk bir kayıt üzerinde pyin çalıştırıp
anlamlıymış gibi bir nota/skor döndürmek, CLAUDE.md'nin "sabit/uydurma sonuç
döndürülmez" kuralını ihlal eder.
**Karar:** `_decode_and_evaluate_quality`, kalite reddedilirse `decoded=None`
döner; `_build_*_analysis` fonksiyonları bu durumda tüm pitch alanlarını
`None`/0 bırakır, pyin hiç çağrılmaz. Test: `test_rejected_recording_does_not_get_fabricated_pitch_fields`.

### K-032: Oturum genelinde tek bir `quality` özeti eklendi (K-025'in tamamlanması)
Aşama 3'te bilerek ertelenen (K-025) oturum geneli `quality` nesnesi artık
gerçek verimiz olduğu için eklendi — CLAUDE.md'deki örnek JSON şemasıyla artık
birebir uyumlu (recommendations hariç, o Aşama 6).
**Karar:** `overall_score`, üç testin en düşük skoru (zincirin en zayıf halkası);
`warnings`, hangi testten geldiği Türkçe önekle belirtilerek birleştiriliyor
(örn. "Konuşma testi: Kayıt çok kısa görünüyor.") — aksi hâlde kullanıcı hangi
kaydı yeniden yapması gerektiğini anlayamaz.

### K-033: `profile` alanı K-025'in aksine Aşama 5'e değil, Aşama 4'e eklendi
K-025, "profile"/"recommendations" alanlarının gerçek pitch verisi olmadan
doldurulamayacağını, ikisinin de sonraki aşamalara bırakılacağını söylüyordu.
Ancak CLAUDE.md'nin Aşama 4 madde listesi "Tahmini profil oluşturma"yı açıkça
Aşama 4'ün kendi kapsamında sayıyor — ve artık gerçek glide/stabilite verisi
elimizde olduğu için ertelemenin bir nedeni kalmadı.
**Karar:** `services/profile_builder.py` eklendi; `recommendations` (şarkı
verisi gerektirdiği için) Aşama 6'ya ertelenmeye devam ediyor. Profil,
yalnızca oturum tamamen kabul edildiyse VE glide aralığı güvenilir şekilde
belirlenebildiyse üretiliyor; aksi hâlde `null` — uydurma profil yok.
Testler (`test_profile_builder.py`) özet metninde kesin/tıbbi ifade veya
klasik ses türü adı (bariton/tenor/soprano) geçmediğini de doğruluyor.
