# Sestiny Song Ingestion Lab

Şarkıların vokal aralığını (ve tessitura'sını) **offline**, yarı otomatik olarak
çıkaran, yalnızca-geliştirici bir araç. Amaç: zaman içinde binlerce şarkılık
doğrulanmış bir katalog kurmak ve yalnızca **insan tarafından onaylanmış** küçük
JSON'u Sestiny production'ına aktarmak.

## Bu neden ayrı bir paket?

Ağır ses-ML bağımlılıkları (torch, onnxruntime, demucs, roformer, rmvpe)
**yalnızca burada** yaşar — Sestiny backend'ine (`../../backend`) hiç girmez.
Böylece production build'i (Render) hafif kalır ve canlı uygulama bu ağır
yığından etkilenmez. Bu araç yalnızca senin Mac'inde, yeni şarkı eklerken çalışır.

## Sınırlar

- Bu araç ses dosyası **edinmez/indirmez**. Kendi (yasal olarak eriştiğin)
  dosyalarını bir klasöre koyarsın, araç onları işler.
- Bir kaydın nota aralığı, `review_status = approved` ve `human_verified = true`
  olmadan production'a **export edilmez**. Bu, verinin dürüstlük kapısıdır.

## Kurulum (Faz 1'de, ayrı venv)

```bash
cd tools/song_ingestion
python3.12 -m venv venv
venv/bin/pip install -r requirements.txt
```

> Faz 0'da (iskelet) ağır bağımlılıklar KURULMAZ. `models.py`, `notes.py`,
> `catalog.py`, `batch.py` yalnızca standart kütüphaneyle çalışır ve test edilir.
> Ağır modeller (ayrıştırma/pitch) Faz 1'de kurulur ve `ingest/` içindeki
> ilgili modüller onları **fonksiyon içinde** (lazy) import eder — bu yüzden
> bağımlılıklar kurulmadan da paket import edilebilir/test edilebilir.

## Katmanlar

| Modül | İş |
| --- | --- |
| `models.py` | `LabSong` + enum'lar (vocal_mode, source_type, review_status) |
| `notes.py` | Hz ↔ MIDI ↔ nota adı (backend/music_theory'nin saf kopyası) |
| `catalog.py` | SQLite katalog: durum, resume, review state |
| `decode.py` | Ses → standart mono dizi (PyAV) |
| `ingest/separate.py` | Vokal ayrıştırma (RoFormer / Demucs, seçilebilir) — Faz 1 |
| `ingest/pitch.py` | F0 + frame güveni (RMVPE / FCPE / pyin) — Faz 1 |
| `ingest/segment.py` | sung/rap segment sınıflama (F0 stabilite) — Faz 1 |
| `ingest/range.py` | robust min/max + tessitura — Faz 1 |
| `ingest/confidence.py` | ölçülen kaliteden güven — Faz 1 |
| `ingest/pipeline.py` | aşamaları birleştirir | 
| `batch.py` | klasör tara → sıraya al → tek tek işle → özet (resume) |
| `review/` | yerel FastAPI + admin arayüzü — Faz 3 |
| `calibrate.py` | singingcarrots'a karşı doğruluk ölçümü — Faz 2 |
| `export.py` | onaylı kayıtları production JSON'una projekte eder |

Ayrıntılı plan ve gerekçeler: `docs/DECISIONS.md` (K-064+) ve konuşma planı.
