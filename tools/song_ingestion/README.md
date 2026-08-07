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

| Modül | İş | Durum |
| --- | --- | --- |
| `models.py` | `LabSong` + enum'lar | ✅ |
| `notes.py` | Hz ↔ MIDI ↔ nota adı | ✅ |
| `catalog.py` | SQLite katalog (durum/resume/review) | ✅ |
| `decode.py` | Ses → mono dizi (PyAV) + content hash | ✅ |
| `config.py` | Analiz eşikleri (merkezî, açıklamalı) | ✅ |
| `ingest/pitch.py` | F0 + frame güveni (RMVPE, ONNX, torch'suz) | ✅ Direct |
| `ingest/note_segments.py` | Frame → güvenilir nota segmentleri | ✅ |
| `ingest/range.py` | Full range (uç-nota eşiği) + tessitura | ✅ |
| `ingest/confidence.py` | Ölçüm-tabanlı güven | ✅ |
| `ingest/engine.py` | Direct RMVPE motoru + debug raporu | ✅ |
| `ingest/separate.py` | Vokal ayrıştırma (RoFormer/Demucs) | ⏳ Pipeline B (benchmark sonrası) |
| `ingest/segment.py` | sung/rap sınıflama | ⏳ sonraki faz |
| `ingest/pipeline.py` | Direct+Separated birleştirici | ⏳ |
| `batch.py` | klasör tara → işle → özet (resume) | ✅ iskelet |
| `export.py` | onaylı → production JSON | ✅ |
| `review/` | yerel FastAPI admin arayüzü | ⏳ Faz 3 |
| `calibrate.py` | singingcarrots doğruluk ölçümü | ⏳ Faz 2 |

Analiz eşikleri ve yöntemleri: `docs/ANALYSIS_THRESHOLDS.md`.
Kararlar/gerekçeler: `docs/DECISIONS.md` (K-064 … K-069).

### Direct RMVPE motorunu çalıştırma (lab venv)

```python
from tools.song_ingestion.ingest.engine import analyze_audio, build_debug_report
# audio: mono float32 numpy dizisi, sample_rate ile
result = analyze_audio(audio, sample_rate)
print(build_debug_report(result))
```

Motor mantığı (segmentasyon/range/tessitura/confidence) sentetik frame'lerle
backend/.venv ile test edilir; gerçek RMVPE testi lab venv gerektirir
(`test_rmvpe_integration.py`, `importorskip`).
