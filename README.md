# Sestiny

Sestiny, kullanıcıdan üç kısa ses kaydı alarak **tahmini bir ses profili** çıkaran ve
bu profile uygun şarkılar önermeyi hedefleyen, web tabanlı bir uygulamadır.

> **Önemli:** Sestiny bir sağlık uygulaması, tıbbi analiz aracı veya profesyonel vokal
> teşhis sistemi **değildir**. Ürettiği sonuçlar yaklaşık değerlendirmelerdir; mikrofon
> kalitesi, ortam gürültüsü, kayıt tekniği ve o anki ses durumundan etkilenir.

## Durum

✅ **Aşama 7 (Kalite, test, dokümantasyon) tamamlandı.** Uçtan uca akış
çalışıyor: kayıt yap → analiz et → tahmini ses profilini ve sana uygun demo
şarkı önerilerini gör. 46 backend + 33 frontend testi geçiyor. Kalan tek
aşama olan **Aşama 8 (Yayına hazırlık)**, yalnızca ayrıca açık onay verilirse
başlar — bkz. `docs/PROJECT_PLAN.md`.

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

İlk sürümde kullanıcı hesabı, veritabanı, ödeme sistemi ve harici yapay zekâ API'si yoktur.
Uygulama tamamen lokal çalışır.

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

## Gizlilik

Ses kayıtların yalnızca bu analiz için işlenir. İlk sürümde kayıtlar kalıcı olarak
saklanmaz ve analiz tamamlandıktan sonra (başarılı ya da başarısız fark etmez)
geçici dosyalar silinir. Ses içeriği veya ham binary veri hiçbir log seviyesinde
yazılmaz — yalnızca oturum kimliği ve sonuç (kabul/ret) loglanır. Hata mesajlarında
dosya yolu veya teknik iz (traceback) gösterilmez. Kullanıcı hesabı, veritabanı ve
harici bir sunucuya veri gönderimi yoktur; her şey kendi bilgisayarında çalışır.

## Bilinen sınırlamalar

- **Tek bir kaydırma testi gerçek profesyonel tessiturayı kesin belirleyemez.**
  Sonuçlar "tahmini" ve "gözlemlenen" dilinde sunulur, kesin teşhis değildir.
- Tarayıcı mikrofonları genelde otomatik kazanç/gürültü bastırma uygular; bu
  yüzden mutlak ses seviyesi ölçümleri (RMS, peak) cihazdan cihaza değişebilir.
- `librosa.pyin` bazen oktav hatası yapabilir (bir notayı bir oktav yukarı/aşağı
  algılama); kod bunu büyük ölçüde filtreler ama tamamen ortadan kaldırmaz.
- Stabilite skoru ve tahmini profil kategorileri (K-013, bölüm 13/4) **klinik
  veya bilimsel bir standarda dayanmaz** — deneyimsel başlangıç eşikleridir.
- Şarkı önerileri, gerçek doğrulanmış veri eklenene kadar yalnızca 12 demo
  ("Demo Şarkı 1", "Demo Şarkı 2"...) kayıt üzerinden çalışır; gerçek bir müzik
  kütüphanesi değildir.
- Uygulama yalnızca güncel Chrome/Edge/Safari gibi `MediaRecorder` ve
  `getUserMedia` destekleyen tarayıcılarda çalışır; eski tarayıcılarda anlaşılır
  bir "desteklenmiyor" mesajı gösterilir ama kayıt yapılamaz.
- Backend tek bir işlemde (process) çalışır; aynı anda çok sayıda kullanıcının
  yoğun kullanımı için ölçeklenmemiştir (ilk sürüm kapsamı dışı).

## Manuel test kontrol listesi

Otomatik testler (46 backend + 33 frontend testi) her commit'te çalışır, ama bazı
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
