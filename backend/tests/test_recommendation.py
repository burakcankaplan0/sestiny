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
    load_symbtr_songs,
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

    def test_load_songs_combines_all_pools(self):
        combined = load_songs()
        assert len(combined) == len(load_demo_songs()) + len(load_verified_songs()) + len(load_symbtr_songs())

    def test_recommendation_pool_can_include_verified_songs(self):
        """Kullanıcı aralığına iyi uyan gerçek bir şarkı, ilk 10 sonuç içinde çıkabilmeli.

        50-70 MIDI aralığı, birkaç gerçek şarkıyla (ör. "Perfect" 55-68, "Colors" 56-68)
        tam örtüşüyor — bunlar 100 skor alıp üst sıralarda yer almalı.
        """
        results = get_recommendations(user_low_midi=50, user_high_midi=70)
        assert any(item.song.verified for item in results)


def _song(**overrides) -> Song:
    """Testler için varsayılan bir şarkı; yalnızca ilgilenilen alanlar geçilir."""
    defaults = dict(
        id="test-song",
        title="Test Şarkı",
        artist="Test Sanatçı",
        language="en",
        genre="pop",
        min_midi=60,
        max_midi=72,
        difficulty="kolay",
        verified=True,
        source_note="test",
        optional_transposition_limit=None,
    )
    defaults.update(overrides)
    return Song(**defaults)


class TestSourceTierAndConfidence:
    """Kaynak katmanı ve güven ağırlığı (K-059)."""

    def test_confidence_comes_from_tier_table(self):
        assert _song(source_tier=1).confidence == 1.0
        assert _song(source_tier=4).confidence < _song(source_tier=1).confidence

    def test_lower_tier_scores_lower_for_identical_range_fit(self):
        """Aynı aralık uyumunda zayıf kaynaklı şarkı geride kalmalı."""
        strong = score_song(_song(id="a", source_tier=1), user_low_midi=60, user_high_midi=72)
        weak = score_song(_song(id="b", source_tier=4), user_low_midi=60, user_high_midi=72)
        assert strong.match_score > weak.match_score

    def test_existing_songs_default_to_highest_tier(self):
        """Eski JSON kayıtlarında bu alanlar yok; varsayılan en güvenilir katman olmalı."""
        for song in load_verified_songs():
            assert song.source_tier == 1
            assert song.freely_transposable is False


class TestFreeTransposition:
    """Serbest transpoze edilebilen eserler (Türk makam müziği, K-060)."""

    def test_freely_transposable_song_can_shift_beyond_default_limit(self):
        """Notasyondaki mutlak yerleşim kullanıcı aralığından uzak olsa bile eser uyabilmeli."""
        far_above = _song(id="makam", min_midi=79, max_midi=91, freely_transposable=True)
        result = score_song(far_above, user_low_midi=55, user_high_midi=67)
        assert result.match_score == 100
        assert result.transposition_semitones is not None
        assert abs(result.transposition_semitones) > 3

    def test_normal_song_cannot_shift_that_far(self):
        """Serbest olmayan bir şarkı aynı mesafeyi kapatamaz — varsayılan sınır korunur."""
        far_above = _song(id="normal", min_midi=79, max_midi=91, freely_transposable=False)
        result = score_song(far_above, user_low_midi=55, user_high_midi=67)
        assert result.match_score < 100

    def test_symbtr_songs_are_all_freely_transposable_with_attribution(self):
        songs = load_symbtr_songs()
        if not songs:
            return  # veri dosyası henüz üretilmemişse test atlanır
        for song in songs:
            assert song.freely_transposable is True
            assert song.language == "tr"
            assert "MTG/SymbTr" in song.source_note, f"{song.title}: kaynak atfı eksik"
            assert "CC BY-NC-SA" in song.source_note, f"{song.title}: lisans bilgisi eksik"


class TestTessitura:
    """Tessitura önceliği (K-064) — öneri, sesin çoğunlukla gezdiği bölgeyi önemser."""

    def test_no_tessitura_behaves_like_full_range(self):
        """Tessitura None ise skor, mevcut full-range mantığıyla birebir aynı olmalı."""
        song = _song(min_midi=60, max_midi=72)
        assert score_song(song, 60, 72).match_score == 100

    def test_tessitura_fit_scores_high_despite_extreme_full_range(self):
        """Uçları kullanıcı aralığını aşsa da tessitura tam oturuyorsa şarkı yüksek skor alır.

        Kullanıcı 55-67; şarkının tessitura'sı 57-65 (tam içeride) ama full range
        50-79 (uçlar dışarıda). Tessitura önceliği sayesinde şarkı elenmemeli.
        """
        song = _song(min_midi=50, max_midi=79, tessitura_low_midi=57, tessitura_high_midi=65)
        result = score_song(song, 55, 67)
        # Tessitura tam oturuyor; yalnızca full range'in taşan kısmı hafif ceza alır.
        assert result.match_score >= 70

    def test_tessitura_outside_range_scores_low(self):
        """Tessitura kullanıcı aralığının dışındaysa, full range örtüşse bile skor düşük olmalı."""
        song = _song(min_midi=48, max_midi=84, tessitura_low_midi=76, tessitura_high_midi=82)
        result = score_song(song, 55, 67)
        assert result.match_score < 60

    def test_tessitura_fit_beats_full_range_only_fit(self):
        """İki şarkı: biri tessitura'sı oturan, diğeri tessitura'sı kullanıcıdan geniş. İlki üstte olmalı."""
        good = _song(id="good", min_midi=52, max_midi=79, tessitura_low_midi=58, tessitura_high_midi=64)
        edge = _song(id="edge", min_midi=55, max_midi=67, tessitura_low_midi=55, tessitura_high_midi=67)
        good_score = score_song(good, 58, 64).match_score
        edge_score = score_song(edge, 58, 64).match_score
        # 'good'ın tessitura'sı (58-64) kullanıcının bölgesine tam oturuyor; uç
        # notaları tavanlı ikincil cezayla en fazla 15 puan kırar → yüksek kalır.
        # 'edge'in tessitura'sı (55-67) kullanıcıdan geniş, rahat bölgeyi zorluyor.
        assert good_score >= 80
        assert good_score > edge_score


class TestDiversityQuota:
    """Çeşitlilik kotası (K-061) — kalabalık bir grup listeyi süpürmemeli."""

    def test_single_language_cannot_fill_the_whole_list(self):
        """Havuzda Türkçe eser sayısı yabancıları çok aşıyor; yine de karışım gelmeli."""
        results = get_recommendations(user_low_midi=55, user_high_midi=67)
        languages = {item.song.language for item in results}
        assert len(languages) > 1, "Öneriler tek dilden oluşmamalı"

    def test_same_artist_is_not_repeated_excessively(self):
        results = get_recommendations(user_low_midi=55, user_high_midi=67)
        counts: dict[str, int] = {}
        for item in results:
            counts[item.song.artist] = counts.get(item.song.artist, 0) + 1
        assert max(counts.values()) <= 2

    def test_results_remain_sorted_by_score(self):
        results = get_recommendations(user_low_midi=55, user_high_midi=67)
        scores = [item.match_score for item in results]
        assert scores == sorted(scores, reverse=True)
