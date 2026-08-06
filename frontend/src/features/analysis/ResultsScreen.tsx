import type { ReactNode } from "react";

import { ScreenLayout } from "../../components/ScreenLayout";
import { texts } from "../../texts";
import type { AnalyzeSessionResponse } from "../../types/analysis";
import { SongRecommendations } from "./SongRecommendations";
import "./ResultsScreen.css";

interface ResultsScreenProps {
  result: AnalyzeSessionResponse;
  onRestart: () => void;
  onBackToReview: () => void;
}

/** Bu eşiğin altındaki güven skorlarında sonucun yanına temkinli-ol notu eklenir. */
const LOW_CONFIDENCE_THRESHOLD = 0.4;

function confidenceNote(confidence: number): string | null {
  return confidence < LOW_CONFIDENCE_THRESHOLD ? texts.results.lowConfidenceNote : null;
}

export function ResultsScreen({ result, onRestart, onBackToReview }: ResultsScreenProps) {
  if (result.status === "rejected") {
    return (
      <ScreenLayout title={texts.results.rejectedTitle} description={texts.results.rejectedIntro}>
        <ul className="results__warning-list">
          {result.quality.warnings.map((warning) => (
            <li key={warning}>{warning}</li>
          ))}
        </ul>
        <div className="btn-row">
          <button type="button" className="btn btn--primary" onClick={onBackToReview}>
            {texts.results.backToReview}
          </button>
        </div>
      </ScreenLayout>
    );
  }

  const { speech, sustained_vowel: vowel, glide, profile, quality } = result;
  const overallConfidence = Math.min(speech.confidence, vowel.confidence, glide.confidence);

  const observedRange =
    glide.observed_low_note && glide.observed_high_note
      ? `${glide.observed_low_note} – ${glide.observed_high_note}`
      : null;
  const comfortableRange =
    glide.estimated_comfortable_low_note && glide.estimated_comfortable_high_note
      ? `${glide.estimated_comfortable_low_note} – ${glide.estimated_comfortable_high_note}`
      : null;

  return (
    <ScreenLayout title={texts.results.title}>
      <section className="results__profile" aria-labelledby="profile-heading">
        <h2 id="profile-heading" className="results__profile-label">
          {profile ? profile.label : texts.results.profileUnavailable}
        </h2>
        {profile && <p className="results__profile-summary">{profile.summary}</p>}
      </section>

      <div className="results__grid">
        <ResultCard title={texts.results.observedRangeTitle}>
          {observedRange ? (
            <>
              <p className="results__value">{observedRange}</p>
              {glide.range_semitones !== null && (
                <p className="results__sub">{texts.results.semitoneRange(glide.range_semitones)}</p>
              )}
            </>
          ) : (
            <p className="results__value results__value--muted">{texts.results.unavailable}</p>
          )}
          {confidenceNote(glide.confidence) && <p className="results__note">{confidenceNote(glide.confidence)}</p>}
        </ResultCard>

        <ResultCard title={texts.results.comfortableRangeTitle}>
          <p className={comfortableRange ? "results__value" : "results__value results__value--muted"}>
            {comfortableRange ?? texts.results.unavailable}
          </p>
        </ResultCard>

        <ResultCard title={texts.results.speechPitchTitle}>
          {speech.approximate_note && speech.median_f0_hz !== null ? (
            <>
              <p className="results__value">
                {speech.approximate_note} ({speech.median_f0_hz} Hz)
              </p>
              {speech.pitch_variability_semitones !== null && (
                <p className="results__sub">{texts.results.pitchVariability(speech.pitch_variability_semitones)}</p>
              )}
            </>
          ) : (
            <p className="results__value results__value--muted">{texts.results.unavailable}</p>
          )}
        </ResultCard>

        <ResultCard title={texts.results.stabilityTitle}>
          <p className="results__value">{texts.results.stabilityValue(vowel.stability_label, vowel.stability_score)}</p>
        </ResultCard>

        <ResultCard title={texts.results.voicedDurationTitle}>
          <p className="results__value">{texts.results.secondsValue(vowel.voiced_duration_seconds)}</p>
        </ResultCard>

        <ResultCard title={texts.results.qualityTitle}>
          <p className="results__value">{quality.label}</p>
        </ResultCard>

        <ResultCard title={texts.results.confidenceTitle}>
          <p className="results__value">%{Math.round(overallConfidence * 100)}</p>
          {confidenceNote(overallConfidence) && (
            <p className="results__note">{confidenceNote(overallConfidence)}</p>
          )}
        </ResultCard>
      </div>

      {result.recommendations.length > 0 ? (
        <SongRecommendations recommendations={result.recommendations} />
      ) : (
        <section className="results__disclaimer" aria-labelledby="recommendations-unavailable-heading">
          <h2 id="recommendations-unavailable-heading" className="results__disclaimer-title">
            {texts.results.recommendationsUnavailableTitle}
          </h2>
          <p>{texts.results.recommendationsUnavailableText}</p>
        </section>
      )}

      <section className="results__disclaimer" aria-labelledby="disclaimer-heading">
        <h2 id="disclaimer-heading" className="results__disclaimer-title">
          {texts.disclaimer.title}
        </h2>
        <p>{texts.disclaimer.notDiagnosis}</p>
      </section>

      <div className="btn-row">
        <button type="button" className="btn btn--primary" onClick={onRestart}>
          {texts.results.redoAll}
        </button>
      </div>
    </ScreenLayout>
  );
}

interface ResultCardProps {
  title: string;
  children: ReactNode;
}

function ResultCard({ title, children }: ResultCardProps) {
  return (
    <article className="results__card">
      <h3 className="results__card-title">{title}</h3>
      {children}
    </article>
  );
}
