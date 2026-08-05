import { useState } from "react";

import { texts } from "../../texts";
import type { SongRecommendation } from "../../types/analysis";
import "./SongRecommendations.css";

interface SongRecommendationsProps {
  recommendations: SongRecommendation[];
}

type DifficultyFilter = "all" | SongRecommendation["difficulty"];

const DIFFICULTY_OPTIONS: { value: DifficultyFilter; label: string }[] = [
  { value: "all", label: texts.recommendations.difficultyAll },
  { value: "kolay", label: texts.recommendations.difficultyEasy },
  { value: "orta", label: texts.recommendations.difficultyMedium },
  { value: "zor", label: texts.recommendations.difficultyHard },
];

function transpositionHint(semitones: number | null): string | null {
  if (semitones === null || semitones === 0) return null;
  return semitones < 0
    ? texts.recommendations.transposeDown(Math.abs(semitones))
    : texts.recommendations.transposeUp(semitones);
}

export function SongRecommendations({ recommendations }: SongRecommendationsProps) {
  const [difficulty, setDifficulty] = useState<DifficultyFilter>("all");

  const filtered =
    difficulty === "all" ? recommendations : recommendations.filter((item) => item.difficulty === difficulty);

  return (
    <section className="recommendations" aria-labelledby="recommendations-heading">
      <h2 id="recommendations-heading" className="recommendations__title">
        {texts.recommendations.title}
      </h2>
      <p className="recommendations__intro">{texts.recommendations.intro}</p>

      <div className="recommendations__filter" role="group" aria-label={texts.recommendations.difficultyFilterLabel}>
        {DIFFICULTY_OPTIONS.map((option) => (
          <button
            key={option.value}
            type="button"
            className="recommendations__filter-button"
            aria-pressed={difficulty === option.value}
            onClick={() => setDifficulty(option.value)}
          >
            {option.label}
          </button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <p className="recommendations__empty">{texts.recommendations.empty}</p>
      ) : (
        <ul className="recommendations__list">
          {filtered.map((song) => (
            <li key={song.id} className="recommendations__card">
              <div className="recommendations__card-header">
                <div>
                  <p className="recommendations__song-title">{song.title}</p>
                  <p className="recommendations__song-artist">{song.artist}</p>
                </div>
                <span className="recommendations__match">
                  {texts.recommendations.matchLabel(song.match_score)}
                </span>
              </div>

              <div className="recommendations__meta">
                <span className="recommendations__badge">{song.genre}</span>
                <span className="recommendations__badge">{song.difficulty}</span>
                <span className="recommendations__badge">
                  {texts.recommendations.rangeLabel(song.min_note, song.max_note)}
                </span>
                {!song.verified && (
                  <span className="recommendations__badge recommendations__demo-badge">
                    {texts.recommendations.demoBadge}
                  </span>
                )}
              </div>

              {transpositionHint(song.transposition_semitones) && (
                <p className="recommendations__transpose-hint">
                  {transpositionHint(song.transposition_semitones)}
                </p>
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
