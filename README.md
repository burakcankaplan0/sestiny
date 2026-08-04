# Sestiny

Sestiny, kullanıcıdan üç kısa ses kaydı alarak **tahmini bir ses profili** çıkaran ve
bu profile uygun şarkılar önermeyi hedefleyen, web tabanlı bir uygulamadır.

> **Önemli:** Sestiny bir sağlık uygulaması, tıbbi analiz aracı veya profesyonel vokal
> teşhis sistemi **değildir**. Ürettiği sonuçlar yaklaşık değerlendirmelerdir; mikrofon
> kalitesi, ortam gürültüsü, kayıt tekniği ve o anki ses durumundan etkilenir.

## Durum

🚧 Geliştirme aşamasında — **Aşama 1 (Frontend–Backend bağlantısı) tamamlandı.**
Uygulama açılıyor ve backend'e bağlanıyor; ses kaydı özellikleri henüz yok.
Geliştirme planı için `docs/PROJECT_PLAN.md` dosyasına bakın.

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

| Araç | Gereken sürüm | Doğrulandığı sürüm |
| --- | --- | --- |
| Node.js | 20 veya üzeri | 26.6.0 |
| npm | Node ile gelir | 11.18.0 |
| Python | 3.11 veya üzeri | 3.12.13 |
| Git | 2.x | 2.50.1 |
| FFmpeg | *(gerekip gerekmediği Aşama 3'te kesinleşecek)* | — |

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
saklanmaz ve analiz tamamlandıktan sonra silinir. Ses içeriği loglanmaz.

## Belgeler

- `CLAUDE.md` — projenin bağlayıcı geliştirme kuralları
- `docs/PROJECT_PLAN.md` — mimari ve aşama aşama geliştirme planı
- `docs/DECISIONS.md` — alınan teknik kararlar ve gerekçeleri
- `docs/PROGRESS.md` — aşama aşama ilerleme kaydı
