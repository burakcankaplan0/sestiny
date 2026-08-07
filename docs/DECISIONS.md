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

---

## Aşama 5 — 2026-08-05

### K-034: "Analiz ediliyor" mesajları gerçek sunucu aşamalarını değil, yaklaşık bir sırayı temsil ediyor
CLAUDE.md sahte yüzde göstergesi yerine gerçek işlem aşamalarına karşılık gelen
mesajlar istiyor ("Kayıt kalitesi kontrol ediliyor" vb.). Ancak backend tek bir
atomik HTTP isteğinde çalışıyor; frontend'in sunucunun hangi aşamada olduğuna
dair gerçek bir sinyali yok.
**Karar:** Üç mesaj, isteğin süresine göre zamanlı olarak sırayla gösteriliyor
(son mesajda kalıp isteği beklemeye devam ediyor). Bu, kesin bir sunucu
ilerlemesi iddia etmiyor — sahte yüzde göstergesi de kullanılmıyor, CLAUDE.md'nin
asıl amacı (kullanıcıyı gerçek dışı bir kesinlikle yanıltmamak) korunuyor.

### K-035: Sonuç ekranında "genel güven skoru", üç testin en düşüğü olarak hesaplanıyor
Ortalama almak, tek bir düşük güvenli testi (örn. gürültülü bir glide kaydı)
diğer ikisinin arkasına gizleyebilirdi.
**Karar:** Backend'in kalite skorunu birleştirirken kullandığı aynı mantık
(K-032, zincirin en zayıf halkası) burada da uygulanıyor — `Math.min`.

### K-036: Reddedilen oturumda hiçbir veri kartı gösterilmiyor
Kalitesi reddedilen bir testin pitch alanları zaten backend'de `null`
dönüyor (K-031), ama yine de "boş kartlarla dolu bir sonuç ekranı" göstermek
kafa karıştırıcı olurdu.
**Karar:** `status: "rejected"` ise ResultsScreen tamamen farklı, sade bir görünüme
geçiyor: yalnızca hangi testlerin neden reddedildiği (backend'in `quality.warnings`
listesi, hangi testten geldiği önekli) ve "İncelemeye dön" butonu gösteriliyor.

### K-037: Mikrofon seviye göstergesi hatası tüm uygulamayı çökertiyordu — düzeltildi
Tarayıcıda gerçek bir akışla (sahte bir `MediaStream` nesnesiyle) elle test
ederken `useMicrophoneLevel`'ın `AudioContext.createMediaStreamSource`
çağrısının senkron olarak fırlattığı bir hatanın React effect'i içinde
yakalanmadığı, bunun da tüm uygulamayı boş bir sayfaya düşürdüğü görüldü.
**Karar:** Kurulum artık `try/catch` içinde; herhangi bir nedenle başarısız
olursa (gerçek tarayıcılarda nadiren de olsa mümkün — cihaz kaybı, izin geri
alınması vb.) özellik sessizce devre dışı kalır (seviye 0 döner), sayfa
çökmez. Regresyon testi eklendi (`useMicrophoneLevel.test.ts`).

---

## Aşama 6 — 2026-08-05

### K-038: Şarkı önerileri ayrı bir uç nokta değil, `analyze-session` cevabının parçası
CLAUDE.md'nin bölüm 9'daki örnek JSON şeması `recommendations`'ı doğrudan
analiz cevabının içinde gösteriyor; öneriler zaten o oturumun tahmini rahat
bölgesine bağlı, ayrı bir GET isteği yalnızca gereksiz bir gidiş-geliş
eklerdi.
**Karar:** `POST /api/v1/analyze-session` artık `recommendations: []` alanını
da dolduruyor — yalnızca oturum kabul edildiyse VE glide'ın tahmini rahat
bölgesi güvenilir şekilde belirlenebildiyse (aksi hâlde boş liste, uydurma
öneri yok).

### K-039: Ton değiştirme önerisi, kaydırma dışında en az taşmayı üreten kaydırma (-3..+3) brute-force taranarak bulunuyor
Şarkının kendi aralığı ile kullanıcının aralığı arasındaki en iyi hizalamayı
analitik bir formülle (ör. orta noktaları hizalama) hesaplamak yerine, izin
verilen küçük aralıkta (varsayılan ±3 yarı ton) her kaydırmayı deneyip en az
taşmayı vereni seçmek hem daha basit hem de her durumda (şarkı aralığı
kullanıcıdan geniş olsa bile) doğru sonuç veriyor.
**Karar:** `_find_best_shift` fonksiyonu 7 değeri (−3..+3) dener. 0 kaydırma
zaten en iyisiyse (taşma yok veya kaydırma iyileştirmiyor) öneri yapılmaz —
zaten uyan bir şarkı için gereksiz "ton değiştir" uyarısı çıkmaz. Öneri
yalnızca kaydırma taşmayı **sıfıra** indiriyorsa yapılır; "biraz iyileştirdi
ama hâlâ sığmıyor" durumunda ton önerisi yapılmaz, sadece düşük skorla
sıralamada geride kalır (CLAUDE.md adım 5: "çok büyük fark varsa üst
sıralarda önerme" — filtrelemek yerine düşük skorla doğal olarak geride
bırakılıyor).

### K-040: Zorluk, hem eşleşme skorunu hem de (frontend'de) ayrı bir filtreyi etkiliyor
CLAUDE.md hem "Eşleşme skoru" hem de ayrı bir madde olarak "Zorluk filtresi"
listeliyor — bunlar iki farklı şey: biri görünmez bir ağırlıklandırma, diğeri
kullanıcının elle değiştirebileceği bir kontrol.
**Karar:** Backend skor hesaplarken zorluğu hafif bir ceza olarak zaten
kullanıyor (K-025'in devamı). Ayrıca frontend'de zorluk filtresi (Tümü/Kolay/
Orta/Zor) istemci tarafında, backend'in döndürdüğü (en fazla 10) öneri
üzerinde çalışıyor — ek bir istek gerektirmiyor.

### K-041: Şarkının nota adları (min_note/max_note), veri dosyasında saklanmıyor; MIDI'den türetiliyor
CLAUDE.md'nin veri modelinde hem `min_midi`/`max_midi` hem `min_note`/
`max_note` var. İkisini de elle veri dosyasına yazmak, ileride biri
güncellenip diğeri unutulursa tutarsızlık riski taşır.
**Karar:** `demo_songs.json` yalnızca `min_midi`/`max_midi` tutar; nota adları
API cevabı oluşturulurken `music_theory.midi_to_note_name` ile hesaplanır —
tek doğruluk kaynağı.

### K-042: Demo şarkılar açıkça kurgu isimlerle ve `verified: false` ile işaretlendi, frontend'de "Demo veri" rozeti gösteriliyor
CLAUDE.md kabul kriteri: "Demo veriler gerçek/verifiye edilmiş şarkı gibi
sunulmuyor."
**Karar:** 12 demo şarkının tümü "Demo Şarkı N" / "Demo Sanatçı N" adlı,
`verified: false`, açıklayıcı `source_note` alanlı. Frontend her öneri
kartında görünür bir "Demo veri" rozeti gösteriyor ve bölüm girişinde "gerçek,
doğrulanmış bir şarkı listesi değildir" uyarısı var. Test edildi (backend:
`test_demo_songs_are_never_marked_as_verified`, `test_demo_songs_use_clearly_fictional_names`;
frontend: demo rozeti render testi).

---

## Aşama 7 — 2026-08-05

### K-043: `scipy` requirements.txt'de kaldı — kaldırılmayı deneyip gerçekten gerekli olduğu doğrulandı
Kod temizliği taraması sırasında `scipy`'nin hiçbir dosyada doğrudan
`import` edilmediği görüldü ve "kullanılmayan bağımlılık" şüphesiyle
kaldırılmayı denendi.
**Karar:** `pip uninstall scipy` sonrası test paketi 20 testte çöktü —
`librosa.pyin` çalışma zamanında `scipy`'ye ihtiyaç duyuyor (transitive değil,
gerçek bir çalışma zamanı bağımlılığı). scipy geri kuruldu; `requirements.txt`'e
bunun neden orada olduğunu (doğrudan import edilmese de) açıklayan bir yorum
eklendi — gelecekte biri "kullanılmıyor" sanıp yanlışlıkla silmesin diye.

### K-044: Vite şablonundan kalan kullanılmayan dosyalar silindi (kullanıcı onayıyla)
`src/assets/react.svg`, `vite.svg`, `hero.png`, `public/icons.svg` ve
`frontend/README.md` (Vite'ın kendi şablon içeriği) Aşama 1'den beri hiçbir
bileşen tarafından kullanılmıyordu — Aşama 1'in `PROGRESS.md` kaydında "açık
kalan küçük iş" olarak not edilmişti.
**Karar:** Kullanıcıdan açıkça onay alınıp silindi (CLAUDE.md: dosya silme
izin gerektirir). Build ve testler sonrasında tekrar çalıştırılıp hiçbir
şeyin bozulmadığı doğrulandı.

### K-045: Kayıt/inceleme ekranlarındaki `<audio>` elemanlarına `aria-label` eklendi
Erişilebilirlik taramasında, birden fazla ses oynatıcının aynı sayfada
bulunduğu (inceleme ekranı) durumlarda ekran okuyucu kullanıcılarının
hangi oynatıcının hangi teste ait olduğunu ayırt edemeyeceği görüldü —
tarayıcının varsayılan `<audio controls>` etiketi bunu belirtmiyor.
**Karar:** Her `<audio>` elemanına `"{test adı} kaydını dinle"` şeklinde
`aria-label` eklendi (`texts.voiceTest.playbackLabel`).

### K-046: Klavye ile buton aktivasyonu (Enter/Space) bu ortamda kesin olarak doğrulanamadı
Erişilebilirlik kontrolü sırasında Tab ile odaklanmanın ve `:focus-visible`
halkasının doğru çalıştığı görsel olarak doğrulandı, ancak bu oturumun
tarayıcı otomasyon aracında gönderilen sentetik `Enter`/`Space` tuş
vuruşları (ve manuel `dispatchEvent` denemesi) butonun `onClick`'ini
tetiklemedi — muhtemelen bu sanal ortamın "trusted event" kısıtlaması.
**Durum:** Kodda hiçbir engelleyici yok (tüm interaktif elemanlar native
`<button>`, `preventDefault` yoktur) — bu, HTML standardı gereği gerçek bir
tarayıcıda çalışması beklenen bir davranıştır, ancak burada kesin olarak
kanıtlanamadı. README'nin manuel test kontrol listesine eklendi; kullanıcının
kendi tarayıcısında bir kez denemesi önerilir. Uydurma bir "doğrulandı"
iddiası yapılmadı (CLAUDE.md: doğrulanamayan şey açıkça belirtilir).

---

## Gerçek şarkı verisi (Aşama 6'nın devamı, plan dışı ek iş) — 2026-08-05

### K-047: Gerçek şarkıların nota aralığı yalnızca web'de bulunan, gösterilebilir bir kaynaktan alındı
CLAUDE.md'nin en katı veri dürüstlüğü kuralı: "gerçek şarkıların nota aralıkları
uydurulmaz." Bu, bir şarkının nota aralığını hafızadan/tahminden yazmanın
kesinlikle yasak olduğu anlamına geliyor — model hafızası güvenilir bir kaynak
değildir.
**Karar:** `singingcarrots.com` (halka açık, vokal eğitimi amaçlı bir şarkı
vokal aralığı veritabanı) üzerinde `WebSearch`/`WebFetch` ile 16 popüler şarkı
arandı; her biri için sitenin kendi şarkı sayfası veya aralık listeleme
sayfası `source_note` alanına URL olarak kaydedildi. Kaynakta bulunamayan
hiçbir şarkı listeye eklenmedi (kullanıcı onayıyla: "kaynak yoksa atla").
Türkçe şarkılar için bu kaynakta veri bulunamadı — bu açıkça belirtildi,
uydurma bir Türkçe liste oluşturulmadı.

### K-048: Zorluk seviyesi, gerçek şarkılarda da nota aralığı genişliğinden otomatik hesaplandı
Kaynak site zorluk derecesini görsel bir gösterge olarak sunuyordu (sayısal
değer API/metin olarak çekilemedi). Elle tahmin etmek yerine, demo şarkılarla
tutarlı ve şeffaf bir kural kullanıldı: ≤13 yarı ton "kolay", 14-19 "orta",
≥20 "zor". Bu, her şarkının `source_note` alanında açıkça belirtildi —
"kaynak sitede zorluk ayrıca listelenmemiştir" notuyla.

### K-049: Gerçek şarkılar demo şarkıların yerine geçmedi, aynı havuza eklendi
Demo verisi (`demo_songs.json`, 12 kayıt) hâlâ geniş bir MIDI aralığını
sistematik olarak kapsıyor ve test/geliştirme için değerli.
**Karar:** Yeni `verified_songs.json` (16 gerçek şarkı) ayrı bir dosyada
tutuldu; `recommendation.py`'deki `load_songs()` ikisini birleştirip tek bir
öneri havuzu oluşturuyor. Frontend'de zaten var olan `verified` alanına göre
rozet gösterme mantığı (K-042) hiçbir değişiklik gerektirmeden gerçek
şarkılarda "Demo veri" rozetini otomatik gizliyor.

### K-050: Öneri bölümü boşsa artık sessizce gizlenmiyor, nedenini açıklayan bir not gösteriyor
Kullanıcı gerçek bir kayıtla denedi ve düşük güvenli bir sonuçta (kaydırma
testinin tahmini rahat bölgesi belirlenemediği için) "Şarkı önerileri"
bölümünün hiçbir açıklama olmadan tamamen kaybolduğunu fark etti — bu, "düşük
güven durumları doğru anlatılıyor" ilkesine (Aşama 5 kabul kriteri) aykırı
sessiz bir boşluktu.
**Karar:** `ResultsScreen`, `recommendations` boşsa artık `results__disclaimer`
stiliyle bir açıklama kutusu gösteriyor: "Kaydırma testinde tahmini rahat
bölgen güvenilir şekilde belirlenemediği için şarkı önerisi oluşturulamadı"
+ testi nasıl daha güvenilir yapabileceğine dair somut bir öneri (sessiz
ortam, sesi zorlamadan yavaşça kaydırma). Test güncellendi.

---

## Aşama 8 — Yayına Hazırlık — 2026-08-06

### K-051: CLAUDE.md'nin "proje tamamen lokal çalışır" kuralı, kullanıcının açık onayıyla gevşetildi
2026-08-06 tarihli `docs/PROGRESS.md` kaydı, kullanıcının o gün "burada
durulsun, uygulama kendi bilgisayarında kullanılacak" kararını verdiğini ve
Aşama 8'in bilinçli olarak başlatılmadığını gösteriyor. Aynı gün içinde
kullanıcı bu kararı değiştirip Aşama 8'e geçmek istediğini ayrıca ve açıkça
belirtti; netleştirme sorusunda "gerçek internet yayını" istediğini ve
hosting için "ücretsiz katman PaaS" tercih ettiğini söyledi.
**Karar:** `CLAUDE.md`'nin "Proje tamamen lokal çalışır" maddesi şu şekilde
değiştirildi: proje varsayılan olarak lokal geliştirilir, ama kullanıcının
Aşama 8 için ayrıca onayıyla ücretsiz katman PaaS'ta (Render + Vercel)
yayınlanabilir. CLAUDE.md'nin diğer tüm kısıtları (hesap yok, veritabanı
yok, ödeme yok, harici AI API yok, Docker yok, Supabase yok) hiçbir
değişiklik olmadan geçerliliğini koruyor — yayına almak bu kısıtların
hiçbirini ihlal etmiyor, yalnızca "yalnızca localhost'ta çalışır" kısıtını
gevşetiyor. Somut hosting çifti olarak Render (backend) + Vercel (frontend)
seçildi — ikisi de ücretsiz katmanda Python/Vite'ı destekliyor, otomatik
HTTPS veriyor. Gerçek hesap açma/repo bağlama/deploy adımları yapay zekâ
asistanı tarafından yapılamaz (hesap oluşturma yasak eylemler arasında) —
bu adımlar README'de kullanıcı için numaralı bir kontrol listesi olarak
bırakıldı.

### K-052: `Settings.debug` varsayılanı `True`'dan `False`'a çevrildi
Uygulama herkese açık internete çıkacağı için, `SESTINY_DEBUG` env var'ı
unutularak deploy edilen bir ortamın güvenli tarafta kalması isteniyor.
Ancak bu değişikliğin gerçekte ne yaptığı konusunda net olmak gerekiyor:
`main.py` `settings.debug`'ı hiçbir zaman FastAPI'nin kendi (traceback
sızdıran) debug moduna bağlamıyor — yalnızca log seviyesini (DEBUG/INFO)
belirliyor (bkz. `configure_logging`). FastAPI'nin traceback sızıntısı zaten
Aşama 7'de doğrulanmıştı (varsayılan `debug=False`, hiç değişmedi).
**Karar:** `debug: bool = True` → `debug: bool = False`. Bu "bir traceback
sızıntısını kapatmak" değil, "ayarlanmamış bir ortamda gereksiz ayrıntılı
log basılmaması" anlamına geliyor — yorum satırında bu netlik korundu. Yerel
geliştirme etkilenmiyor: `backend/.env.example` zaten `SESTINY_DEBUG=true`
öneriyor, geliştirici bunu `.env`'e kopyaladığında eskisi gibi ayrıntılı log
görmeye devam ediyor.

### K-053: Hız sınırlama `slowapi` ile, IP başına 5/dakika, yalnızca `analyze-session` uç noktasında
CPU-yoğun `POST /api/v1/analyze-session` (librosa pitch analizi) herkese
açık internete çıktığında korumasız kalıyordu; `docs/PROGRESS.md` bunu
zaten Aşama 8 konusu olarak öngörmüştü. Redis gibi harici bir servis
kurmak, backend zaten tek process çalıştığı için (bkz. README "Bilinen
sınırlamalar") gereksiz bir karmaşıklık olurdu.
**Karar:** `slowapi` (bellek içi, `limits` kütüphanesi üzerine kurulu)
eklendi. Eşik `app/core/config.py`'de `ANALYZE_SESSION_RATE_LIMIT = "5/minute"`
adlı, açıklamalı bir sabit (CLAUDE.md: sihirli sayı yasağı burada da
uygulandı). Limiter yalnızca `analyze-session` route dekoratörüne
uygulandı — `health` gibi ucuz uç noktalar sınırlanmadı. 429 cevabı özel
bir handler'la (`app/core/rate_limit.py`) Türkçe, ham hata sızdırmayan bir
mesaja çevriliyor (`RATE_LIMIT_MESSAGE`), frontend `client.ts` bunu ayrı bir
`texts.errors.rateLimited` mesajına eşliyor. **Test riski ve çözümü:**
tüm backend testleri aynı `TestClient` (aynı sahte IP) üzerinden çalıştığı
için, hız sınırlama olduğu gibi eklenseydi başka test dosyalarındaki
istekler birbirinin limitini sessizce dolduracaktı. `backend/tests/conftest.py`'ye
her testten önce `limiter.reset()` çağıran bir `autouse` fixture eklendi —
bu proje için ilk `conftest.py`.

### K-054: Render'ın `$PORT`'una bağlanmak için kod değil, yalnızca start command değiştirildi
PaaS platformları (Render) kendi `$PORT` env var'ını enjekte edip processin
ona bağlanmasını bekler. Uygulamanın zaten bir Python giriş noktası
(`if __name__ == "__main__"`) yok — `uvicorn app.main:app --reload` her
zaman CLI'dan çalıştırılıyor (bkz. `main.py` docstring'i).
**Karar:** Koda hiç dokunulmadı. `render.yaml`'ın `startCommand`'i doğrudan
`uvicorn app.main:app --host 0.0.0.0 --port $PORT` kullanıyor —
`SESTINY_HOST`/`SESTINY_PORT` ayarları yerel geliştirme için olduğu gibi
kalıyor (varsayılan `127.0.0.1:8000`), deploy ortamında hiç okunmuyorlar.
Bu, `Settings`'e platform-özel bir `PORT` okuma mantığı eklemekten daha
basit ve yerel/deploy davranışını birbirinden net şekilde ayırıyor.

### K-055: Test bağımlılıkları (`pytest`, `httpx`) `requirements.txt`'den ayrı bir dosyaya bölünmedi
Prod build'e test araçlarının da kurulması ilk bakışta gereksiz gibi
görünüyor. Ancak bunu ayırmak (`requirements-dev.txt`) iki dosyanın
senkron tutulmasını, README'nin kurulum komutunun güncellenmesini ve
`render.yaml`'ın hangi dosyayı kullanacağının netleştirilmesini gerektirir
— küçük, saf Python paketlerinin (birkaç MB) prod imajına girmesinin
gerçek maliyeti bu karmaşıklığa değmiyor.
**Karar:** `requirements.txt` tek dosya olarak kaldı (K-043'teki gibi:
düşünüldü, gerekçesiyle bilinçli olarak atlandı).

### K-056: `numpy==2.5.1` pini gerçekte kurulu olan sürümle uyuşmuyordu — Render'daki ilk gerçek deploy denemesi bunu ortaya çıkardı
Kullanıcı README'deki adımları takip edip gerçek bir Render hesabıyla ilk
canlı deploy'u denedi — bu, projenin ilk kez gerçek bir üçüncü parti
altyapıda build edilme denemesiydi. Build başarısız oldu. Log incelenince
kök neden anlaşıldı: `requirements.txt`'te `numpy==2.5.1` yazıyordu, ama
yerel `.venv`'de (ve tüm otomatik testlerin geçtiği ortamda) gerçekte kurulu
olan `numpy==2.4.6` idi — muhtemelen `librosa`'nın çalışma zamanı bağımlılığı
`numba` kurulurken pip'in sessizce farklı bir numpy sürümüne yerleştiği bir
an oldu ve `requirements.txt` o an güncellenmedi. Yerelde bu fark hiç fark
edilmedi çünkü `pip install -r requirements.txt` bir daha sıfırdan
çalıştırılmadı. Render'da pip, `numpy==2.5.1`'i harfiyen kurmaya çalışırken
ona uyumlu bir `numba` sürümü arayışına girdi; uyumlu, Python 3.12 için
hazır paketi (wheel) olan bir sürüm bulamayınca eskiye doğru "geri arama"
yaptı ve sonunda Python 3.12'yi hiç desteklemeyen çok eski bir `numba`
sürümüne düşüp build'i çökertti.
**Karar:** `numpy` pini gerçekte test edilen sürüme (`2.4.6`) düzeltildi;
ayrıca `numba==0.66.0` ve `llvmlite==0.48.0` da (daha önce örtük/geçişli
bağımlılık olan, ama gerçekte kritik olan `scipy` gibi, bkz. K-043)
açıkça pinlendi — böylece pip'in bu paketler arasında bir uyum "araması"
gerekmiyor, doğrudan bilinen çalışan kombinasyonu kuruyor. Düzeltme,
sıfırdan bir `.venv` ile (Render'ın yapacağı gibi) yerel olarak yeniden
denenip 55/55 testin geçtiği doğrulandıktan sonra push edildi. **Ders:**
bir bağımlılık pip tarafından örtük şekilde değiştiğinde (elle
`pip install` ile ya da başka bir paketin transitive çözümlemesiyle),
`requirements.txt` hemen `pip freeze` ile karşılaştırılıp güncellenmeli —
aksi hâlde yerelde çalışan bir kurulum, temiz bir ortamda (CI, PaaS)
sessizce farklı davranabiliyor.

---

## Şarkı havuzu genişletmesi — 2026-08-06

### K-057: 13 yeni gerçek şarkı eklendi; Türkçe şarkı için hâlâ kaynak bulunamadı
Kullanıcı hem daha fazla yabancı hem Türkçe gerçek şarkı istedi. K-047'nin
kuralı (gerçek şarkı aralığı yalnızca gösterilebilir bir kaynaktan alınır,
hafızadan uydurulmaz) burada da harfiyen uygulandı.
**Yabancı şarkılar:** `singingcarrots.com`'da 13 yeni şarkı doğrulandı (The
Beatles, Whitney Houston, John Legend, Michael Jackson, Bruno Mars, Sam
Smith, Coldplay, Billie Eilish, Guns N' Roses, Frank Sinatra, Louis
Armstrong, BTS, Toto) — her biri gerçek şarkı sayfası URL'i ile
`verified_songs.json`'a eklendi (toplam 16 → 29). Aralıklar farklı ses
tiplerini kapsayacak şekilde seçildi: en düşük Sweet Child o' Mine (F#2),
en dar/kolay bad guy (11 yarı ton), en geniş Sweet Child o' Mine (33 yarı
ton, verse ile Axl Rose'un üst register çığlıklarını birlikte kapsadığı
için).
**Türkçe şarkılar:** Bu sefer daha kapsamlı arandı — `singingcarrots.com`'un
tüm sanatçı listesi tarandı, Tarkan/Sezen Aksu/Ajda Pekkan/Zeki
Müren/Ahmet Kaya/MFÖ için doğrudan sayfa/arama denendi, alternatif kaynaklar
(tessitura siteleri, akor/BPM siteleri) araştırıldı. **Hiçbir kaynakta
Türkçe şarkı için gerçek nota aralığı verisi bulunamadı** — akor/BPM
siteleri (Tunebat, SongBPM) yalnızca müzikal tonu (key) veriyor, bu gerçek
söylenen nota aralığıyla aynı şey değil, o yüzden kullanılmadı.
**Karar:** K-047'deki karar aynen geçerliliğini koruyor — kaynak yoksa
Türkçe şarkı eklenmiyor, uydurma veri oluşturulmuyor. Bu durum
`docs/PROGRESS.md`'ye tekrar açıkça not edildi; ileride güvenilir bir
Türkçe kaynak bulunursa (ör. bir Türk vokal koçunun yayınladığı bir liste)
kolayca eklenebilir — veri modeli buna zaten hazır (`language` alanı).

### K-058: Telifli ses dosyalarını indirip analiz etme fikri reddedildi; bunun yerine büyük bir singingcarrots.com taraması yapıldı
Kullanıcı, Spotify Türkiye Top 50 gibi listelerden şarkı dosyalarını
indirip Sestiny'nin kendi analiz motoruyla ölçmeyi önerdi ("ben dosyaları
sana atayım, telif sorununu kendim hallederim"). İki gerekçeyle reddedildi:
(1) Telifli ticari kaydı indirmenin (Spotify/YouTube fark etmeksizin)
yasal bir yolu yok — Spotify Premium'un çevrimdışı indirmesi bile DRM
şifreli, analiz edilebilir bir dosya vermiyor; kullanıcının "sorumluluğu
üstlenmesi" bunu değiştirmiyor çünkü dosyayı işleyip sonucu canlı siteye
yükleyecek olan yapay zekâ asistanının kendisi. (2) Sestiny'nin
`librosa.pyin` tabanlı analiz motoru tek, temiz bir ses için tasarlandı
(K-008); davul/bas/gitar/çoklu vokal içeren tam prodüksiyonlu bir kayıtta
çalıştırılırsa muhtemelen enstrüman frekanslarını yanlışlıkla nota
sanıp hatalı bir aralık üretir — bunu `verified: true` diye yayınlamak,
uydurma kadar zararlı bir güvenilirlik yanılsaması yaratırdı.
**Karar:** Bunun yerine `singingcarrots.com`'da (zaten K-047'den beri
kullanılan, insan tarafından belirlenmiş/yayınlanmış gerçek kaynak) çok
daha büyük bir tarama yapıldı: tek tek popüler şarkı sayfaları (32 deneme,
~27 başarı) taranarak havuz 29'dan **56 gerçek şarkıya** çıkarıldı — Queen,
Elton John, David Bowie, Whitney Houston, Beyoncé, Taylor Swift, Nirvana,
U2, ABBA, The Beatles, Fleetwood Mac, Amy Winehouse ve daha fazlası.
Ayrıca `singingcarrots.com`'un "bu aralıktaki şarkılar" listeleme
sayfaları da denendi (ör. `/vocal-range/C3-C5`) ama bunlar çoğunlukla az
tanınan kilise/ilahi şarkıları çıkardı — kullanıcının istediği "yüksek
popülerlik" kriterine uymadığı için o sonuçlar kullanılmadı, yalnızca
tek tek doğrulanan tanınmış hit şarkılar eklendi.

---

## Türkçe şarkı havuzu — SymbTr aktarımı — 2026-08-07

### K-059: Şarkı verisine kaynak katmanı (`source_tier`) ve güven ağırlığı eklendi
Havuz artık tek bir kaynaktan gelmiyor: yayınlanmış vokal aralığı
veritabanı (singingcarrots), makine okunur nota verisi (SymbTr), ileride
ölçüm veya kulakla bildirim. Bunları eşit güvenilirlikte saymak yanlış
olurdu; ama düşük güvenli veriyi tamamen dışlamak da havuzun büyümesini
imkânsız kılıyordu — her yeni kaynak "ya hep ya hiç" kararına dönüşüyordu.
**Karar:** `Song`'a `source_tier` alanı eklendi (1: yayınlanmış veritabanı,
2: makine okunur nota, 3: ölçüm, 4: kulakla bildirim, 5: demo). Güven,
kayda ayrıca yazılmaz — `config.SOURCE_TIER_CONFIDENCE` tablosundan
türetilen bir `property`'dir, böylece iki yerin tutarsızlaşma riski yok.
Eşleşme skoru bu güvenle çarpılır: zayıf kaynaklı veri havuza girer ama
aynı aralık uyumunda güçlü kaynaklının önüne geçemez. Alanların varsayılan
değeri olduğu için mevcut 68 kaydın JSON'ları değiştirilmedi.

### K-060: Türk makam eserleri "serbest transpoze edilebilir" olarak modellendi — sabit bir mutlak aralık atanmadı
SymbTr'ın MIDI dosyalarından çıkarılan aralıkların medyanı G4–C6, merkezi
~D5 çıktı — insan sesi için absürt derecede tiz. Sebep bir veri hatası
değil: Türk makam müziğinde eser teorik bir referans perdeden notaya
alınır, gerçek icrada perde seviyesini ("ahenk") icracı kendi sesine göre
seçer. Yani bu eserlerin **sabit bir mutlak nota aralığı yoktur**; yalnızca
aralık genişliği (medyan 17 yarı ton) anlamlıdır.
Sabit bir düzeltme (ör. "hepsini 12 yarı ton indir") uydurma olurdu ve
CLAUDE.md'nin veri dürüstlüğü kuralını çiğnerdi.
**Karar:** `Song`'a `freely_transposable` alanı eklendi. Bu eserler
eşleştirmede ±36 yarı tona kadar serbestçe kaydırılır (ilk denenen ±12
yetersiz kaldı: pes bir ses için gereken kaydırma 24 yarı tonu aşabiliyor).
Arayüz bu eserlerde sayısal bir yarı ton önerisi göstermez — "-29 yarı ton
aşağıdan dene" anlamsız olurdu; yerine "bu eser sesine uygun perdeden
söylenir; sabit bir tonu yoktur" der. Her kaydın `source_note` alanında
bunun bir referans olduğu, "şu notalarda söylenir" iddiası olmadığı açıkça
yazılı.

### K-061: Öneri sonuçlarına dil ve sanatçı kotası eklendi
Havuza 1586 Türkçe eser eklenince yeni bir sorun doğdu: serbest transpoze
edilebildikleri için hepsi yüksek skor alıyor ve ilk 10 sonucun tamamını
dolduruyorlardı — kullanıcı bir daha hiç yabancı şarkı göremeyecekti.
Aynı şekilde tek bir bestecinin (Ahmet Avni Konuk'un 120 eseri) listeyi
doldurma riski vardı.
**Karar:** `get_recommendations()` skor sırasını koruyarak dil başına en
fazla 6, sanatçı başına en fazla 2 sonuç alıyor. Kota yüzünden liste eksik
kalırsa (havuzda gerçekten tek dil varsa) atlananlardan tamamlanıyor, yani
sonuç sayısı azalmıyor. Gerçek bir kayıtla doğrulandı: G2–E4 aralığındaki
bir ses için 6 yabancı + 4 Türkçe öneri geliyor.

### K-062: Demo şarkılar en düşük katmana indirildi, silinmedi
12 demo şarkı ("Demo Şarkı 1"), havuzda gerçek veri yokken algoritmanın
çalıştığını göstermek için vardı (K-042, K-049). Havuz 1654 şarkıya
çıkınca bunlar üst sıraları işgal etmeye başladı — canlı bir sitede gerçek
kullanıcıya uydurma şarkı önermek, mevcut herhangi bir gerçek şarkıdan
kötü. Ayrıca `language: "tr"` etiketli oldukları için dil kotasının Türkçe
slotlarını doldurup gerçek Türkçe eserlerin hiç görünmemesine yol açtılar.
**Karar:** Silinmediler (K-049'daki gerekçe hâlâ geçerli: test ve
geliştirme için değerliler, geniş bir MIDI aralığını sistematik kapsıyorlar)
ama `SOURCE_TIER_DEMO` (güven 0.2) katmanına indirildiler — artık yalnızca
daha iyi bir alternatif yoksa görünürler. Katman veri dosyasına yazılmadı,
`load_demo_songs()` içinde tek yerden atanıyor.

### K-063: Eser adları dosya adından değil MusicXML'den okunuyor
SymbTr dosya adları yalnızca ASCII taşıyor; buradan üretilen başlıklar
Türkçe karakterleri kaybediyordu ("Zulfunu", "Hüseyin" yerine "Huseyin").
**Karar:** Aktarım script'i başlık ve besteci bilgisini aynı eserin
MusicXML dosyasından okuyor ("Zülfünü Tasvîr İçin", "Hacı Ârif Bey").
MusicXML'in başlık dönüşümü kesme işaretinden sonraki ekleri de büyütmüş
olduğu için ("Ordu'Nun") tek bir düzeltme uygulanıyor: kesmeden sonraki
harf küçültülür. MusicXML dosyaları eserin sözlerini de içeriyor, ancak
script yalnızca başlık ve besteci alanlarını okur — sözlere dokunulmaz.
Aynı şekilde eserin sözlü olup olmadığı, txt dosyasındaki söz sütununun
**doluluğu** sayılarak belirlenir; içerik hiçbir yere yazılmaz.
