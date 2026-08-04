# Sestiny

Sestiny, kullanıcıdan üç kısa ses kaydı alarak **tahmini bir ses profili** çıkaran ve
bu profile uygun şarkılar önermeyi hedefleyen, web tabanlı bir uygulamadır.

> **Önemli:** Sestiny bir sağlık uygulaması, tıbbi analiz aracı veya profesyonel vokal
> teşhis sistemi **değildir**. Ürettiği sonuçlar yaklaşık değerlendirmelerdir; mikrofon
> kalitesi, ortam gürültüsü, kayıt tekniği ve o anki ses durumundan etkilenir.

## Durum

🚧 Geliştirme aşamasında — **Aşama 0 (Ortam ve Plan) tamamlandı.** Henüz çalışan bir
uygulama yoktur. Geliştirme planı için `docs/PROJECT_PLAN.md` dosyasına bakın.

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
| Ses analizi | librosa (`pyin`), NumPy, SciPy, SoundFile |
| Format dönüştürme | FFmpeg *(veya PyAV — Aşama 3'te kesinleşecek)* |
| Testler | pytest (backend), Vitest + Testing Library (frontend) |

İlk sürümde kullanıcı hesabı, veritabanı, ödeme sistemi ve harici yapay zekâ API'si yoktur.
Uygulama tamamen lokal çalışır.

## Gereksinimler

| Araç | Gereken sürüm | Bu makinede |
| --- | --- | --- |
| Node.js | 20 LTS veya üzeri | ❌ kurulu değil |
| npm | Node ile birlikte gelir | ❌ kurulu değil |
| Python | 3.11 veya üzeri | ⚠️ yalnızca 3.9.6 var |
| FFmpeg | güncel sürüm | ❌ kurulu değil |
| Git | 2.x | ✅ 2.50.1 |

Eksik araçların kurulumu Aşama 1 başlamadan yapılacaktır.

## Kurulum ve çalıştırma

> Bu bölüm Aşama 1'de gerçek, doğrulanmış komutlarla doldurulacaktır.
> Henüz `frontend/` ve `backend/` klasörleri oluşturulmadığı için buraya
> çalıştığı doğrulanmamış komut yazılmamıştır.

## Gizlilik

Ses kayıtların yalnızca bu analiz için işlenir. İlk sürümde kayıtlar kalıcı olarak
saklanmaz ve analiz tamamlandıktan sonra silinir. Ses içeriği loglanmaz.

## Belgeler

- `CLAUDE.md` — projenin bağlayıcı geliştirme kuralları
- `docs/PROJECT_PLAN.md` — mimari ve aşama aşama geliştirme planı
- `docs/DECISIONS.md` — alınan teknik kararlar ve gerekçeleri
- `docs/PROGRESS.md` — aşama aşama ilerleme kaydı
