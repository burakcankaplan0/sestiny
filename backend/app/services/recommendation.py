"""Demo şarkı verisiyle basit aralık eşleştirme.

Gerçek şarkı nota aralıkları uydurulmaz (bkz. CLAUDE.md veri dürüstlüğü kuralları).
Burada yalnızca açıkça kurgu "Demo Şarkı" kayıtları kullanılır (`verified: false`);
gerçek/doğrulanmış şarkı listesi ileride bu dosyanın yerini alacak veya ona eklenecek.
"""

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from app.core.config import (
    DIFFICULTY_SCORE_PENALTY,
    MAX_RECOMMENDATIONS,
    OVERSHOOT_PENALTY_PER_SEMITONE,
    TRANSPOSITION_MAX_SEMITONES,
)

DEMO_SONGS_PATH = Path(__file__).resolve().parent.parent / "data" / "demo_songs.json"


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


@dataclass(frozen=True)
class SongRecommendation:
    song: Song
    match_score: int
    # Negatif: aşağıdan (daha pes) çalınması/söylenmesi önerilir. Pozitif: yukarıdan.
    # None: ton değiştirmeye gerek yok ya da küçük bir taşımayla düzelmiyor.
    transposition_semitones: int | None


@lru_cache
def load_demo_songs() -> list[Song]:
    """demo_songs.json'u okuyup Song listesine çevirir. Sonucu önbelleğe alır."""
    raw_entries = json.loads(DEMO_SONGS_PATH.read_text(encoding="utf-8"))
    return [Song(**entry) for entry in raw_entries]


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
    max_shift = min(
        TRANSPOSITION_MAX_SEMITONES,
        song.optional_transposition_limit if song.optional_transposition_limit is not None else TRANSPOSITION_MAX_SEMITONES,
    )
    best_shift, best_overshoot = _find_best_shift(song.min_midi, song.max_midi, user_low_midi, user_high_midi, max_shift)

    score = 100
    score -= best_overshoot * OVERSHOOT_PENALTY_PER_SEMITONE
    score -= DIFFICULTY_SCORE_PENALTY.get(song.difficulty, 0)
    score = max(0, min(100, score))

    # Yalnızca kaydırma gerçekten taşmayı sıfıra indiriyorsa öneri yapılır;
    # "en iyisi buydu ama yine de sığmıyor" durumunda ton değiştirme önerilmez.
    transposition_semitones = best_shift if (best_shift != 0 and best_overshoot == 0) else None

    return SongRecommendation(song=song, match_score=score, transposition_semitones=transposition_semitones)


def get_recommendations(
    user_low_midi: int,
    user_high_midi: int,
    limit: int = MAX_RECOMMENDATIONS,
) -> list[SongRecommendation]:
    """Tüm demo şarkıları puanlar, en iyi eşleşenden başlayarak sıralar."""
    songs = load_demo_songs()
    scored = [score_song(song, user_low_midi, user_high_midi) for song in songs]
    scored.sort(key=lambda item: item.match_score, reverse=True)
    return scored[:limit]
