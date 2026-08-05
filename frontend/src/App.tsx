import { useCallback, useEffect, useState } from "react";

import { MicrophoneCheck } from "./features/microphone-check/MicrophoneCheck";
import { useMicrophoneStream } from "./features/microphone-check/useMicrophoneStream";
import { WelcomeScreen } from "./features/onboarding/WelcomeScreen";
import { RecordingsReview } from "./features/voice-tests/RecordingsReview";
import { VOICE_TESTS } from "./features/voice-tests/testConfig";
import { VoiceTestScreen } from "./features/voice-tests/VoiceTestScreen";
import { useBackendHealth } from "./hooks/useBackendHealth";
import { texts } from "./texts";
import type { RecordingResult, RecordingsState, TestId } from "./types/recording";

type Step = "welcome" | "mic-check" | TestId | "review";

const TEST_ORDER: TestId[] = VOICE_TESTS.map((test) => test.id);

const EMPTY_RECORDINGS: RecordingsState = {
  speech: null,
  sustained_vowel: null,
  glide: null,
};

function App() {
  const [step, setStep] = useState<Step>("welcome");
  const [recordings, setRecordings] = useState<RecordingsState>(EMPTY_RECORDINGS);
  // Kullanıcı incelemeden bir testi yeniden kaydetmeye gittiğinde, bitince incelemeye geri dönmesi için.
  const [returnToReview, setReturnToReview] = useState(false);
  const [analyzeMessage, setAnalyzeMessage] = useState<string | null>(null);

  const health = useBackendHealth();
  const microphone = useMicrophoneStream();

  const hasAnyRecording = Object.values(recordings).some((recording) => recording !== null);

  // Kayıt varken sayfa yanlışlıkla yenilenirse kullanıcı uyarılır.
  useEffect(() => {
    if (!hasAnyRecording) return undefined;

    const handleBeforeUnload = (event: BeforeUnloadEvent) => {
      event.preventDefault();
      event.returnValue = "";
    };

    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => window.removeEventListener("beforeunload", handleBeforeUnload);
  }, [hasAnyRecording]);

  const handleRecordingChange = useCallback((testId: TestId, recording: RecordingResult | null) => {
    setRecordings((previous) => ({ ...previous, [testId]: recording }));
  }, []);

  const handleContinueFromTest = useCallback(
    (testId: TestId) => {
      if (returnToReview) {
        setReturnToReview(false);
        setStep("review");
        return;
      }
      const currentIndex = TEST_ORDER.indexOf(testId);
      const nextTestId = TEST_ORDER[currentIndex + 1];
      setStep(nextTestId ?? "review");
    },
    [returnToReview],
  );

  const handleReRecordFromReview = useCallback((testId: TestId) => {
    setReturnToReview(true);
    setAnalyzeMessage(null);
    setStep(testId);
  }, []);

  const handleAnalyze = useCallback(() => {
    setAnalyzeMessage(texts.review.analyzeComingSoon);
  }, []);

  if (step === "welcome") {
    return (
      <WelcomeScreen
        healthStatus={health.status}
        healthMessage={health.message}
        onRetryHealth={health.retry}
        onStart={() => setStep("mic-check")}
      />
    );
  }

  if (step === "mic-check") {
    return (
      <MicrophoneCheck
        status={microphone.status}
        errorMessage={microphone.errorMessage}
        isSupported={microphone.isSupported}
        stream={microphone.stream}
        onRequestAccess={microphone.requestAccess}
        onContinue={() => setStep("speech")}
      />
    );
  }

  if (step === "review") {
    return (
      <RecordingsReview
        recordings={recordings}
        onReRecord={handleReRecordFromReview}
        onAnalyze={handleAnalyze}
        analyzeMessage={analyzeMessage}
      />
    );
  }

  const testIndex = TEST_ORDER.indexOf(step);
  const testConfig = VOICE_TESTS[testIndex];
  const isLastTest = testIndex === TEST_ORDER.length - 1;
  const continueLabel = returnToReview
    ? texts.voiceTest.backToReview
    : isLastTest
      ? texts.voiceTest.goToReview
      : texts.voiceTest.nextTest;

  return (
    <VoiceTestScreen
      config={testConfig}
      stepIndex={testIndex + 1}
      totalSteps={TEST_ORDER.length}
      stream={microphone.stream}
      existingRecording={recordings[step]}
      onRecordingChange={handleRecordingChange}
      onContinue={() => handleContinueFromTest(step)}
      continueLabel={continueLabel}
    />
  );
}

export default App;
