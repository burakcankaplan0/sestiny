"""recommendation.py testleri.

CLAUDE.md Aşama 6 kabul kriterlerini doğrudan karşılar: demo verilerden tutarlı
öneriler, kullanıcı aralığı değişince sıralama değişiyor, ton önerisi
matematiksel olarak doğru, demo veriler gerçek/doğrulanmış gibi sunulmuyor.
"""

from app.services.recommendation import (
    Song,
    get_recommendations,
    load_demo_songs,
    load_songs,
    load_verified_songs,
    score_song,
)


def _song(
    *,
    song_id: str = "test-song",
    min_midi: int = 50,
    max_midi: int = 62,
    difficulty: str = "kolay",
    optional_transposition_limit: int | None = None,
) -> Song:
    return Song(
        id=song_id,
        title="Test Şarkısı",
        artist="Test Sanatçı",
        language="tr",
        genre="pop",
        min_midi=min_midi,
        max_midi=max_midi,
        difficulty=difficulty,
        verified=False,
        source_note="Demo veri — gerçek bir şarkı değildir.",
        optional_transposition_limit=optional_transposition_limit,
    )


class TestScoreSong:
    def test_song_fully_within_range_gets_top_score(self):
        song = _song(min_midi=52, max_midi=60)
        result = score_song(song, user_low_midi=48, user_high_midi=64)

        assert result.match_score == 100
        assert result.transposition_semitones is None

    def test_song_two_semitones_too_high_gets_transposition_suggestion(self):
        # Şarkı 50-62, kullanıcı 48-60: şarkı üstten 2 yarı ton taşıyor.
        song = _song(min_midi=50, max_midi=62)
        result = score_song(song, user_low_midi=48, user_high_midi=60)

        # 2 yarı ton aşağı kaydırınca (50-2=48, 62-2=60) tam sığıyor.
        assert result.transposition_semitones == -2
        assert result.match_score == 100

    def test_song_two_semitones_too_low_suggests_upward_transposition(self):
        song = _song(min_midi=44, max_midi=56)
        result = score_song(song, user_low_midi=46, user_high_midi=58)

        assert result.transposition_semitones == 2
        assert result.match_score == 100

    def test_song_far_beyond_transposition_limit_gets_low_score_no_suggestion(self):
        # Şarkı aralığı kullanıcının çok üstünde (10 yarı ton), 3 yarı tonluk
        # taşımayla düzelmiyor — öneri yapılmaz, skor düşük olur ama şarkı elenmez.
        song = _song(min_midi=70, max_midi=80)
        result = score_song(song, user_low_midi=48, user_high_midi=60)

        assert result.transposition_semitones is None
        assert result.match_score < 50

    def test_already_fitting_song_gets_no_unnecessary_transposition_suggestion(self):
        song = _song(min_midi=50, max_midi=58)
        result = score_song(song, user_low_midi=48, user_high_midi=64)

        assert result.transposition_semitones is None

    def test_harder_difficulty_lowers_score_at_equal_fit(self):
        easy = score_song(_song(min_midi=50, max_midi=60, difficulty="kolay"), user_low_midi=48, user_high_midi=64)
        hard = score_song(_song(min_midi=50, max_midi=60, difficulty="zor"), user_low_midi=48, user_high_midi=64)

        assert hard.match_score < easy.match_score

    def test_song_specific_transposition_limit_is_respected(self):
        # Şarkı 5 yarı ton taşıyor ama kendi optional_transposition_limit'i 2 —
        # genel sınır 3 olsa bile bu şarkı için 2'nin ötesinde kaydırma denenmez.
        song = _song(min_midi=50, max_midi=62, optional_transposition_limit=2)
        result = score_song(song, user_low_midi=45, user_high_midi=57)

        assert result.transposition_semitones is None
        assert result.match_score < 100

    def test_score_never_negative(self):
        song = _song(min_midi=20, max_midi=30, difficulty="zor")
        result = score_song(song, user_low_midi=70, user_high_midi=80)

        assert result.match_score >= 0


class TestGetRecommendations:
    def test_demo_data_produces_consistent_recommendations(self):
        first = get_recommendations(user_low_midi=50, user_high_midi=64)
        second = get_recommendations(user_low_midi=50, user_high_midi=64)

        assert [item.song.id for item in first] == [item.song.id for item in second]
        assert len(first) > 0

    def test_results_sorted_by_score_descending(self):
        results = get_recommendations(user_low_midi=48, user_high_midi=60)
        scores = [item.match_score for item in results]

        assert scores == sorted(scores, reverse=True)

    def test_changing_user_range_changes_ranking(self):
        low_voice_results = get_recommendations(user_low_midi=38, user_high_midi=52)
        high_voice_results = get_recommendations(user_low_midi=62, user_high_midi=76)

        top_low = low_voice_results[0].song.id
        top_high = high_voice_results[0].song.id

        assert top_low != top_high

    def test_demo_songs_are_never_marked_as_verified(self):
        """Demo veriler gerçek/doğrulanmış şarkı gibi sunulmamalı."""
        for song in load_demo_songs():
            assert song.verified is False
            assert song.source_note

    def test_demo_songs_use_clearly_fictional_names(self):
        for song in load_demo_songs():
            assert song.title.startswith("Demo Şarkı")
            assert song.artist.startswith("Demo Sanatçı")

    def test_returns_at_most_ten_results_by_default(self):
        results = get_recommendations(user_low_midi=40, user_high_midi=76)
        assert len(results) <= 10


class TestVerifiedSongs:
    """Gerçek, dış kaynaklı şarkı verisi (verified_songs.json) için doğruluk testleri."""

    def test_at_least_one_verified_song_exists(self):
        assert len(load_verified_songs()) > 0

    def test_every_verified_song_is_marked_verified_with_a_real_source(self):
        for song in load_verified_songs():
            assert song.verified is True
            # source_note uydurma olmadığını göstermek için gerçek bir URL içermeli.
            assert "http" in song.source_note, f"{song.title}: source_note bir kaynak URL'i içermeli"

    def test_verified_song_ranges_are_internally_consistent(self):
        for song in load_verified_songs():
            assert song.min_midi < song.max_midi, f"{song.title}: min_midi max_midi'den küçük olmalı"
            # Makul bir insan sesi aralığı dışına taşan bir değer, veri girişi hatasına işaret eder.
            assert 24 <= song.min_midi <= 96
            assert 24 <= song.max_midi <= 96

    def test_load_songs_combines_demo_and_verified_pools(self):
        combined = load_songs()
        assert len(combined) == len(load_demo_songs()) + len(load_verified_songs())

    def test_recommendation_pool_can_include_verified_songs(self):
        """Kullanıcı aralığına iyi uyan gerçek bir şarkı, ilk 10 sonuç içinde çıkabilmeli.

        50-70 MIDI aralığı, birkaç gerçek şarkıyla (ör. "Perfect" 55-68, "Colors" 56-68)
        tam örtüşüyor — bunlar 100 skor alıp üst sıralarda yer almalı.
        """
        results = get_recommendations(user_low_midi=50, user_high_midi=70)
        assert any(item.song.verified for item in results)
