import { ScreenLayout } from "../../components/ScreenLayout";
import { texts } from "../../texts";
import { VOICE_TESTS } from "./testConfig";
import type { RecordingsState, TestId } from "../../types/recording";
import "./RecordingsReview.css";

interface RecordingsReviewProps {
  recordings: RecordingsState;
  onReRecord: (testId: TestId) => void;
  onAnalyze: () => void;
  analyzeMessage: string | null;
}

export function RecordingsReview({ recordings, onReRecord, onAnalyze, analyzeMessage }: RecordingsReviewProps) {
  const allComplete = VOICE_TESTS.every((test) => recordings[test.id] !== null);

  return (
    <ScreenLayout title={texts.review.title} description={texts.review.intro}>
      <ul className="review__list">
        {VOICE_TESTS.map((test) => {
          const recording = recordings[test.id];
          return (
            <li className="review__item" key={test.id}>
              <div className="review__item-header">
                <span className="review__item-title">{test.title}</span>
                <span
                  className={`review__badge ${recording ? "review__badge--done" : "review__badge--missing"}`}
                >
                  {recording ? texts.review.statusDone : texts.review.statusMissing}
                </span>
              </div>

              {recording && (
                <audio
                  className="voice-test__player"
                  controls
                  src={recording.url}
                  data-testid={`review-audio-${test.id}`}
                />
              )}

              <button type="button" className="btn btn--secondary" onClick={() => onReRecord(test.id)}>
                {texts.review.reRecordButton}
              </button>
            </li>
          );
        })}
      </ul>

      <div className="review__analyze">
        <button type="button" className="btn btn--primary" onClick={onAnalyze} disabled={!allComplete}>
          {texts.review.analyzeButton}
        </button>
        {!allComplete && <p className="review__hint">{texts.review.analyzeDisabledHint}</p>}
        {analyzeMessage && (
          <p className="review__hint" role="status" aria-live="polite">
            {analyzeMessage}
          </p>
        )}
      </div>
    </ScreenLayout>
  );
}
