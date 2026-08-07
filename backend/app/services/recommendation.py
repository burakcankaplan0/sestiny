"""Şarkı verisiyle basit aralık eşleştirme.

Gerçek şarkı nota aralıkları uydurulmaz (bkz. CLAUDE.md veri dürüstlüğü kuralları).
İki veri dosyası birleştirilerek kullanılır:
- `demo_songs.json`: açıkça kurgu "Demo Şarkı" kayıtları (`verified: false`) —
  test/geliştirme amaçlı, geniş bir MIDI aralığını sistematik olarak kapsar.
- `verified_songs.json`: gerçek şarkılar (`verified: true`); her birinin nota
  aralığı, `source_note` alanında belirtilen dış bir kaynaktan alınmıştır
  (bkz. docs/DECISIONS.md K-047) — hiçbir değer hafızadan/tahminden yazılmadı.
"""

import json
from dataclasses import dataclass, replace
from functools import lru_cache
from pathlib import Path

from app.core.config import (
    DIFFICULTY_SCORE_PENALTY,
    FREE_TRANSPOSITION_MAX_SEMITONES,
    FULL_RANGE_SECONDARY_MAX_PENALTY,
    FULL_RANGE_SECONDARY_PENALTY_PER_SEMITONE,
    MAX_RECOMMENDATIONS,
    MAX_RECOMMENDATIONS_PER_ARTIST,
    MAX_RECOMMENDATIONS_PER_LANGUAGE,
    OVERSHOOT_PENALTY_PER_SEMITONE,
    SOURCE_TIER_CONFIDENCE,
    SOURCE_TIER_DEMO,
    SOURCE_TIER_PUBLISHED_RANGE,
    SOURCE_TIER_REPORTED_BY_EAR,
    TRANSPOSITION_MAX_SEMITONES,
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DEMO_SONGS_PATH = DATA_DIR / "demo_songs.json"
VERIFIED_SONGS_PATH = DATA_DIR / "verified_songs.json"
SYMBTR_SONGS_PATH = DATA_DIR / "symbtr_songs.json"


@dataclass(frozen=True)
class Song:
    id: str
    title: str
    artist: str
    language: str
    genre: str
    min_midi: int
    max_midi: int
    difficulty: str
    verified: bool
    source_note: str
    optional_transposition_limit: int | None
    # Verinin hangi tür kaynaktan geldiği (bkz. config.SOURCE_TIER_*). Eski
    # kayıtlarda bulunmayabileceği için varsayılanı en güvenilir katman.
    source_tier: int = SOURCE_TIER_PUBLISHED_RANGE
    # Eserin sabit bir mutlak aralığı yoksa (Türk makam müziği: perde seviyesi
    # icracının seçtiği "ahenk"e göre değişir) serbestçe kaydırılabilir.
    freely_transposable: bool = False
    # Tessitura: şarkının büyük bölümünde kalınan temel vokal bölge. min/max
    # (full range) uç notaları içerir (ad-lib, tek bir tiz çığlık); tessitura
    # ise "sesin çoğunlukla nerede gezdiği". Öneri eşleştirmesi tessitura'yı
    # önceler (bkz. K-064). Yalnızca ses analizinden gelen kayıtlarda dolu olur;
    # eski kayıtlarda None → full range mantığına düşülür.
    tessitura_low_midi: int | None = None
    tessitura_high_midi: int | None = None
    # Parçanın vokal karakteri (sung / melodic_rap / rap / mixed). Öneri metni
    # ve ileride filtreleme için. Eski kayıtlar söylenen eserlerdir.
    vocal_mode: str = "sung"

    @property
    def confidence(self) -> float:
        """Kaynak katmanına karşılık gelen güven (0-1). Tek doğruluk kaynağı
        config'teki tablodur — her kayda ayrıca yazılmaz, tutarsızlık riski olmasın."""
        return SOURCE_TIER_CONFIDENCE.get(self.source_tier, SOURCE_TIER_CONFIDENCE[SOURCE_TIER_REPORTED_BY_EAR])


@dataclass(frozen=True)
class SongRecommendation:
    song: Song
    match_score: int
    # Negatif: aşağıdan (daha pes) çalınması/söylenmesi önerilir. Pozitif: yukarıdan.
    # None: ton değiştirmeye gerek yok ya da küçük bir taşımayla düzelmiyor.
    transposition_semitones: int | None


def _load_songs_from(path: Path) -> list[Song]:
    raw_entries = json.loads(path.read_text(encoding="utf-8"))
    return [Song(**entry) for entry in raw_entries]


@lru_cache
def load_demo_songs() -> list[Song]:
    """Yalnızca demo_songs.json'u okur (verified=false). Sonucu önbelleğe alır.

    Demo veri tanımı gereği en düşük kaynak katmanındadır — katman veri
    dosyasına yazılmaz, burada tek yerden atanır ki 12 kaydın hepsinde
    tekrarlanıp tutarsızlaşma riski olmasın.
    """
    return [replace(song, source_tier=SOURCE_TIER_DEMO) for song in _load_songs_from(DEMO_SONGS_PATH)]


@lru_cache
def load_verified_songs() -> list[Song]:
    """Yalnızca verified_songs.json'u okur (verified=true, dış kaynaklı). Sonucu önbelleğe alır."""
    return _load_songs_from(VERIFIED_SONGS_PATH)


@lru_cache
def load_symbtr_songs() -> list[Song]:
    """SymbTr'dan aktarılan Türkçe eserler. Dosya yoksa boş liste döner —
    aktarım script'i henüz çalıştırılmamış olabilir, bu uygulamayı çökertmemeli."""
    if not SYMBTR_SONGS_PATH.exists():
        return []
    return _load_songs_from(SYMBTR_SONGS_PATH)


@lru_cache
def load_songs() -> list[Song]:
    """Öneri havuzu: demo + doğrulanmış yabancı + SymbTr Türkçe eserler. Önbelleğe alınır."""
    return load_demo_songs() + load_verified_songs() + load_symbtr_songs()


def _overshoot(song_low: int, song_high: int, user_low: int, user_high: int, shift: int) -> int:
    """Şarkı `shift` kadar kaydırıldığında kullanıcı aralığının kaç yarı ton dışına taştığını döndürür."""
    shifted_low = song_low + shift
    shifted_high = song_high + shift
    low_overshoot = max(0, user_low - shifted_low)
    high_overshoot = max(0, shifted_high - user_high)
    return low_overshoot + high_overshoot


def _find_best_shift(song_low: int, song_high: int, user_low: int, user_high: int, max_shift: int) -> tuple[int, int]:
    """-max_shift..+max_shift arasında (0 dahil) en az taşma üreten kaydırmayı bulur.

    0 kaydırması zaten en iyisiyse (taşma yoksa veya kaydırma iyileştirmiyorsa) 0 döner —
    zaten uyan bir şarkı için gereksiz ton değiştirme önerisi yapılmaz.
    """
    best_shift = 0
    best_overshoot = _overshoot(song_low, song_high, user_low, user_high, 0)
    for shift in range(-max_shift, max_shift + 1):
        if shift == 0:
            continue
        overshoot = _overshoot(song_low, song_high, user_low, user_high, shift)
        if overshoot < best_overshoot:
            best_overshoot = overshoot
            best_shift = shift
    return best_shift, best_overshoot


def score_song(song: Song, user_low_midi: int, user_high_midi: int) -> SongRecommendation:
    """Şarkının kullanıcı aralığına ne kadar uyduğunu 0-100 skora çevirir.

    Adımlar CLAUDE.md bölüm 5'teki algoritmayı izler: aralık örtüşmesi → skor,
    1-3 yarı ton taşmada ton değiştirme önerisi, kalan büyük taşmalarda düşük skor
    (şarkı filtrelenmez, sadece sıralamada geride kalır), zorluk skora dahil edilir.
    """
    if song.freely_transposable:
        # Makam müziğinde eserin mutlak perdesi icracıya aittir; notasyondaki
        # yerleşim bir referanstır, sınır değil (bkz. K-060).
        max_shift = FREE_TRANSPOSITION_MAX_SEMITONES
    else:
        max_shift = min(
            TRANSPOSITION_MAX_SEMITONES,
            song.optional_transposition_limit if song.optional_transposition_limit is not None else TRANSPOSITION_MAX_SEMITONES,
        )
    # Birincil eşleştirme hedefi: tessitura varsa o (sesin çoğunlukla gezdiği
    # bölge), yoksa full range. Böylece skor öncelikle "rahat bölge" uyumuyla
    # belirlenir (bkz. K-064). Tessitura yoksa davranış eskisiyle birebir aynı.
    if song.tessitura_low_midi is not None and song.tessitura_high_midi is not None:
        primary_low, primary_high = song.tessitura_low_midi, song.tessitura_high_midi
    else:
        primary_low, primary_high = song.min_midi, song.max_midi

    best_shift, best_overshoot = _find_best_shift(primary_low, primary_high, user_low_midi, user_high_midi, max_shift)

    score = 100
    score -= best_overshoot * OVERSHOOT_PENALTY_PER_SEMITONE

    # Tessitura kullanıldıysa, full range'in tessitura ötesinde taşan kısmı
    # (uç/ad-lib notalar) yalnızca hafif ikincil bir ceza alır.
    if song.tessitura_low_midi is not None and song.tessitura_high_midi is not None:
        full_overshoot = _overshoot(song.min_midi, song.max_midi, user_low_midi, user_high_midi, best_shift)
        extra_beyond_tessitura = max(0, full_overshoot - best_overshoot)
        score -= min(
            FULL_RANGE_SECONDARY_MAX_PENALTY,
            extra_beyond_tessitura * FULL_RANGE_SECONDARY_PENALTY_PER_SEMITONE,
        )

    score -= DIFFICULTY_SCORE_PENALTY.get(song.difficulty, 0)
    # Kaynağı daha zayıf olan veri, aynı aralık uyumunda geride kalır — havuza
    # girer ama üst sıraları işgal etmez (bkz. K-059).
    score = round(score * song.confidence)
    score = max(0, min(100, score))

    # Yalnızca kaydırma gerçekten taşmayı sıfıra indiriyorsa öneri yapılır;
    # "en iyisi buydu ama yine de sığmıyor" durumunda ton değiştirme önerilmez.
    transposition_semitones = best_shift if (best_shift != 0 and best_overshoot == 0) else None

    return SongRecommendation(song=song, match_score=score, transposition_semitones=transposition_semitones)


def _apply_diversity_quota(scored: list[SongRecommendation], limit: int) -> list[SongRecommendation]:
    """Skor sırasını koruyarak dil ve sanatçı kotası uygular.

    Havuzda bir grup (ör. 1500+ Türkçe makam eseri) diğerlerini sayıca çok
    aşabiliyor; kota olmasa bu grup listenin tamamını doldurur ve kullanıcı tek
    tip öneri görür. Kota dolunca o gruptaki şarkılar atlanır, sıradaki farklı
    gruptan şarkı yukarı çıkar (bkz. K-061).

    Yeterli çeşitlilik yoksa (ör. havuzda gerçekten tek dil varsa) liste kotayla
    kısıtlanıp eksik kalmaz: ikinci geçişte atlananlardan tamamlanır.
    """
    selected: list[SongRecommendation] = []
    skipped: list[SongRecommendation] = []
    language_counts: dict[str, int] = {}
    artist_counts: dict[str, int] = {}

    for item in scored:
        if len(selected) >= limit:
            break
        language = item.song.language
        artist = item.song.artist
        if (
            language_counts.get(language, 0) >= MAX_RECOMMENDATIONS_PER_LANGUAGE
            or artist_counts.get(artist, 0) >= MAX_RECOMMENDATIONS_PER_ARTIST
        ):
            skipped.append(item)
            continue
        selected.append(item)
        language_counts[language] = language_counts.get(language, 0) + 1
        artist_counts[artist] = artist_counts.get(artist, 0) + 1

    # Kota yüzünden liste eksik kaldıysa, en iyi atlananlarla tamamla.
    if len(selected) < limit:
        selected.extend(skipped[: limit - len(selected)])
        selected.sort(key=lambda item: item.match_score, reverse=True)

    return selected


def get_recommendations(
    user_low_midi: int,
    user_high_midi: int,
    limit: int = MAX_RECOMMENDATIONS,
) -> list[SongRecommendation]:
    """Havuzdaki tüm şarkıları puanlar, en iyi eşleşenden sıralar, çeşitlilik kotası uygular."""
    songs = load_songs()
    scored = [score_song(song, user_low_midi, user_high_midi) for song in songs]
    scored.sort(key=lambda item: item.match_score, reverse=True)
    return _apply_diversity_quota(scored, limit)
