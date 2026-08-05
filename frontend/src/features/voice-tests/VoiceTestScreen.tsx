import { useCallback } from "react";

import { ScreenLayout } from "../../components/ScreenLayout";
import { texts } from "../../texts";
import { formatSeconds } from "../../utils/time";
import { useAudioRecorder } from "./useAudioRecorder";
import type { VoiceTestConfig } from "./testConfig";
import type { RecordingResult, TestId } from "../../types/recording";
import "./VoiceTestScreen.css";

interface VoiceTestScreenProps {
  config: VoiceTestConfig;
  stepIndex: number;
  totalSteps: number;
  stream: MediaStream | null;
  existingRecording: RecordingResult | null;
  onRecordingChange: (testId: TestId, recording: RecordingResult | null) => void;
  onContinue: () => void;
  continueLabel: string;
}

export function VoiceTestScreen({
  config,
  stepIndex,
  totalSteps,
  stream,
  existingRecording,
  onRecordingChange,
  onContinue,
  continueLabel,
}: VoiceTestScreenProps) {
  const handleComplete = useCallback(
    (result: RecordingResult) => onRecordingChange(config.id, result),
    [config.id, onRecordingChange],
  );

  const { phase, elapsedSeconds, start, stop } = useAudioRecorder(stream, config.maxSeconds, handleComplete);

  const handleDelete = useCallback(() => {
    if (existingRecording) URL.revokeObjectURL(existingRecording.url);
    onRecordingChange(config.id, null);
  }, [config.id, existingRecording, onRecordingChange]);

  const handleReRecord = useCallback(() => {
    handleDelete();
    start();
  }, [handleDelete, start]);

  const hasRecording = existingRecording !== null;
  const meetsMinimum = hasRecording && existingRecording.durationSeconds >= config.minSeconds;
  const isRecording = phase === "recording";

  return (
    <ScreenLayout
      eyebrow={texts.voiceTest.progress(stepIndex, totalSteps)}
      title={config.title}
      description={config.instruction}
    >
      {config.sentenceToRead ? (
        <blockquote className="voice-test__sentence">“{config.sentenceToRead}”</blockquote>
      ) : null}

      <p className="voice-test__duration-hint">
        {texts.voiceTest.recommendedDuration(config.recommendedMinSeconds, config.recommendedMaxSeconds)}
      </p>

      <div className="voice-test__recorder" role="group" aria-label={config.title}>
        <div className="voice-test__timer">
          {formatSeconds(isRecording ? elapsedSeconds : (existingRecording?.durationSeconds ?? 0))}
        </div>

        <p className="voice-test__status" role="status" aria-live="polite">
          {isRecording
            ? texts.voiceTest.recordingInProgress
            : hasRecording
              ? texts.voiceTest.recordingSaved
              : ""}
        </p>

        {!hasRecording && !isRecording && (
          <button type="button" className="btn btn--primary" onClick={start} disabled={!stream}>
            {texts.voiceTest.startButton}
          </button>
        )}

        {isRecording && (
          <button type="button" className="btn btn--primary" onClick={stop}>
            {texts.voiceTest.stopButton}
          </button>
        )}

        {hasRecording && !isRecording && existingRecording && (
          <>
            <audio
              className="voice-test__player"
              controls
              src={existingRecording.url}
              aria-label={texts.voiceTest.playbackLabel(config.title)}
              data-testid="playback-audio"
            />
            <div className="btn-row">
              <button type="button" className="btn btn--secondary" onClick={handleReRecord}>
                {texts.voiceTest.reRecordButton}
              </button>
              <button type="button" className="btn btn--danger" onClick={handleDelete}>
                {texts.voiceTest.deleteButton}
              </button>
            </div>
          </>
        )}
      </div>

      {hasRecording && !meetsMinimum && (
        <p className="voice-test__warning" role="alert">
          {texts.voiceTest.minDurationHint(config.minSeconds)}
        </p>
      )}

      <div className="btn-row voice-test__continue-row">
        <button type="button" className="btn btn--primary" onClick={onContinue} disabled={!meetsMinimum}>
          {continueLabel}
        </button>
      </div>
    </ScreenLayout>
  );
}
