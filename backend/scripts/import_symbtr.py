"""SymbTr veri setinden Türkçe şarkı havuzu üretir.

Kaynak: https://github.com/MTG/SymbTr (Creative Commons BY-NC-SA 4.0)
Bu, uygulamanın çalışma zamanının parçası DEĞİLDİR — veri dosyasını bir kez
üretmek için elle çalıştırılan bir hazırlık aracıdır. Üretilen dosya
(`app/data/symbtr_songs.json`) depoya işlenir; SymbTr deposunun kendisi
projeye kopyalanmaz.

Kullanım (backend/ klasöründen):
    .venv/bin/python scripts/import_symbtr.py /yol/SymbTr

Önemli tasarım kararları:
- **Serbest transpoze (K-060):** Türk makam müziğinde eserin sabit bir mutlak
  perde aralığı yoktur; icracı kendi sesine uygun "ahenk"i seçer. Notasyondaki
  yerleşim teorik bir referanstır. Bu yüzden aktarılan aralık "bu eser şu
  notalarda söylenir" iddiası değildir; yalnızca aralık GENİŞLİĞİ anlamlıdır ve
  eşleştirme sırasında eser serbestçe kaydırılır.
- **Sözlü eser tespiti:** Form adına güvenilmez (aynı form hem sözlü hem
  enstrümantal olabilir). Bunun yerine txt dosyasındaki söz sütununun dolu olup
  olmadığına bakılır. Söz İÇERİĞİ hiçbir yere yazılmaz, yalnızca varlığı sayılır.
- **Dinî formlar** kullanıcı isteğiyle tamamen dışarıda bırakılır.
"""

import csv
import json
import re
import sys
import unicodedata
import xml.etree.ElementTree as ElementTree
from pathlib import Path

import mido

# Dinî repertuvar — kullanıcı isteğiyle havuza alınmıyor.
RELIGIOUS_FORMS = {
    "ilahi", "nefes", "durak", "tevsih", "sugul", "mersiye", "naat", "kaside",
    "miraciye", "ayin", "savt", "tesbih", "salat", "temcit", "mevlevi", "münacat",
    "munacat", "ezan", "sala", "gulbank", "tekbir",
}

# Söz sütununda gerçek hece sayılmayan işaretler.
NON_LYRIC_TOKENS = {".", "-", "_", "", "0"}

# Bir eserin "sözlü" sayılması için gereken en az gerçek hece sayısı.
MIN_LYRIC_SYLLABLES = 5

# Analiz için anlamlı sayılan en az nota sayısı.
MIN_NOTE_COUNT = 20

# Bundan geniş bir aralık, tek bir vokal partisi için fiziksel olarak
# anlamsızdır — büyük ihtimalle veri hatası veya çok sesli/karma kayıt.
MAX_PLAUSIBLE_RANGE_SEMITONES = 40

# Zorluk, aralık genişliğinden hesaplanır — demo ve diğer gerçek şarkılarla
# tutarlı olsun diye aynı kural (bkz. K-048).
DIFFICULTY_EASY_MAX_SEMITONES = 13
DIFFICULTY_MEDIUM_MAX_SEMITONES = 19

SOURCE_URL = "https://github.com/MTG/SymbTr"
LICENSE_NOTE = "CC BY-NC-SA 4.0"


def difficulty_for_range(semitones: int) -> str:
    if semitones <= DIFFICULTY_EASY_MAX_SEMITONES:
        return "kolay"
    if semitones <= DIFFICULTY_MEDIUM_MAX_SEMITONES:
        return "orta"
    return "zor"


def humanize(raw: str) -> str:
    """`ordunun_dereleri` → `Ordunun Dereleri`. Boşsa boş string döner."""
    cleaned = raw.replace("_", " ").strip()
    if not cleaned:
        return ""
    return " ".join(word.capitalize() for word in cleaned.split())


def slugify(raw: str) -> str:
    """Şarkı id'si için ASCII slug üretir (Türkçe karakterler sadeleştirilir)."""
    normalized = unicodedata.normalize("NFKD", raw)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "-", ascii_only).strip("-")


def metadata_from_musicxml(xml_path: Path) -> tuple[str, str]:
    """MusicXML'den (eser adı, besteci) döndürür; okunamazsa ("", "").

    Dosya adları yalnızca ASCII olduğu için Türkçe karakterleri kaybediyor
    ("Zulfunu"); MusicXML ise düzgün yazımı taşıyor ("Zülfünü"). Yalnızca
    başlık ve besteci alanları okunur — eserin sözlerine hiç dokunulmaz.
    """
    try:
        root = ElementTree.parse(xml_path).getroot()
    except (OSError, ElementTree.ParseError):
        return "", ""

    title_element = root.find("./work/work-title")
    title = (title_element.text or "").strip() if title_element is not None else ""
    # SymbTr başlıkları her kelimeyi büyük harfle başlatan bir dönüşümden geçmiş;
    # bu, kesme işaretinden sonraki Türkçe ekleri de yanlışlıkla büyütmüş
    # ("Ordu'Nun"). Türkçede kesmeden sonraki ek daima küçük harfle yazılır.
    title = re.sub(r"(?<=')(\w)", lambda match: match.group(1).lower(), title)

    composer = ""
    for creator in root.findall("./identification/creator"):
        if creator.get("type") == "composer":
            composer = (creator.text or "").strip()
            break

    return title, composer


def has_lyrics(txt_path: Path) -> bool:
    """Eserin sözlü olup olmadığını söz sütununun doluluğundan anlar.

    Sözlerin kendisi okunmaz/saklanmaz — yalnızca kaç hücrenin dolu olduğu sayılır.
    """
    try:
        with txt_path.open(encoding="utf-8", errors="ignore") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            found = 0
            for row in reader:
                token = (row.get("Soz1") or "").strip()
                if token and token not in NON_LYRIC_TOKENS:
                    found += 1
                    if found >= MIN_LYRIC_SYLLABLES:
                        return True
    except OSError:
        return False
    return False


def note_range(midi_path: Path) -> tuple[int, int] | None:
    """MIDI dosyasındaki en pes ve en tiz notayı döndürür; okunamazsa None."""
    try:
        midi_file = mido.MidiFile(midi_path)
    except (OSError, ValueError, EOFError, IndexError):
        # Bozuk/eksik MIDI dosyaları sessizce atlanır — hangi dosya olduğu
        # çağıran tarafta raporlanır.
        return None

    notes = [
        message.note
        for track in midi_file.tracks
        for message in track
        if message.type == "note_on" and message.velocity > 0
    ]
    if len(notes) < MIN_NOTE_COUNT:
        return None
    return min(notes), max(notes)


def build_song(midi_path: Path, txt_dir: Path, xml_dir: Path) -> dict | None:
    """Tek bir SymbTr eserini şarkı kaydına çevirir; uygun değilse None döner."""
    stem = midi_path.stem
    parts = stem.split("--")
    if len(parts) < 5:
        return None

    makam, form, usul, name, composer = parts[0], parts[1], parts[2], parts[3], parts[4]

    if form in RELIGIOUS_FORMS:
        return None
    if not has_lyrics(txt_dir / f"{stem}.txt"):
        return None

    found_range = note_range(midi_path)
    if found_range is None:
        return None
    low, high = found_range
    span = high - low
    if span == 0 or span > MAX_PLAUSIBLE_RANGE_SEMITONES:
        return None

    # Türkçe yazımı doğru olan MusicXML tercih edilir; yoksa dosya adına düşülür.
    xml_title, xml_composer = metadata_from_musicxml(xml_dir / f"{stem}.xml")
    title = xml_title or humanize(name)
    if not title:
        return None
    artist = xml_composer or humanize(composer) or "Anonim"
    # SymbTr'da besteci bilinmeyen eserler köşeli parantezle işaretlenmiş.
    if artist.startswith("[") and artist.endswith("]"):
        artist = artist.strip("[]").strip() or "Anonim"

    return {
        "id": f"symbtr-{slugify(stem)}",
        "title": title,
        "artist": artist,
        "language": "tr",
        "genre": humanize(form).lower() or "türk müziği",
        "min_midi": low,
        "max_midi": high,
        "difficulty": difficulty_for_range(span),
        "verified": True,
        "source_note": (
            f"Kaynak: SymbTr Türk makam müziği veri seti ({SOURCE_URL}), {LICENSE_NOTE}. "
            f"Dosya: {stem}. Makam: {humanize(makam)}, usul: {humanize(usul)}. "
            "Aralık, eserin makine okunur notasından hesaplanmıştır. "
            "Türk makam müziğinde eserin mutlak perdesi sabit değildir — icracı "
            "kendi sesine uygun ahengi seçer; bu yüzden buradaki notalar bir "
            "referanstır, 'bu eser şu notalarda söylenir' iddiası değildir. "
            "Zorluk, aralık genişliğinden hesaplanmıştır."
        ),
        "optional_transposition_limit": None,
        "source_tier": 2,
        "freely_transposable": True,
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("Kullanım: python scripts/import_symbtr.py /yol/SymbTr", file=sys.stderr)
        return 1

    symbtr_root = Path(sys.argv[1]).expanduser().resolve()
    midi_dir = symbtr_root / "midi"
    txt_dir = symbtr_root / "txt"
    xml_dir = symbtr_root / "MusicXML"
    if not midi_dir.is_dir() or not txt_dir.is_dir():
        print(f"SymbTr klasöründe midi/ ve txt/ bulunamadı: {symbtr_root}", file=sys.stderr)
        return 1

    songs: list[dict] = []
    seen_ids: set[str] = set()
    skipped = 0

    for midi_path in sorted(midi_dir.glob("*.mid")):
        song = build_song(midi_path, txt_dir, xml_dir)
        if song is None:
            skipped += 1
            continue
        if song["id"] in seen_ids:
            skipped += 1
            continue
        seen_ids.add(song["id"])
        songs.append(song)

    output_path = Path(__file__).resolve().parent.parent / "app" / "data" / "symbtr_songs.json"
    output_path.write_text(
        json.dumps(songs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"Aktarılan eser: {len(songs)}")
    print(f"Atlanan (dinî/enstrümantal/okunamayan/tekrar): {skipped}")
    print(f"Yazıldı: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
