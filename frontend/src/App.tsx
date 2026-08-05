import { useCallback, useEffect, useState } from "react";

import { submitAnalysisSession } from "./api/analysis";
import { ApiError } from "./api/client";
import { AnalyzingScreen } from "./features/analysis/AnalyzingScreen";
import { ResultsScreen } from "./features/analysis/ResultsScreen";
import { MicrophoneCheck } from "./features/microphone-check/MicrophoneCheck";
import { useMicrophoneStream } from "./features/microphone-check/useMicrophoneStream";
import { WelcomeScreen } from "./features/onboarding/WelcomeScreen";
import { RecordingsReview } from "./features/voice-tests/RecordingsReview";
import { VOICE_TESTS } from "./features/voice-tests/testConfig";
import { VoiceTestScreen } from "./features/voice-tests/VoiceTestScreen";
import { useBackendHealth } from "./hooks/useBackendHealth";
import { texts } from "./texts";
import type { AnalyzeSessionResponse } from "./types/analysis";
import type { RecordingResult, RecordingsState, TestId } from "./types/recording";
import { ScreenLayout } from "./components/ScreenLayout";

type Step = "welcome" | "mic-check" | TestId | "review" | "analyzing" | "results";

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
  const [analysisResult, setAnalysisResult] = useState<AnalyzeSessionResponse | null>(null);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [analysisAttempt, setAnalysisAttempt] = useState(0);

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

  // "analyzing" adımına girildiğinde (veya tekrar denendiğinde) üç kaydı backend'e gönderir.
  useEffect(() => {
    if (step !== "analyzing") return undefined;

    const { speech, sustained_vowel: sustainedVowel, glide } = recordings;
    if (!speech || !sustainedVowel || !glide) {
      // Buton yalnızca üçü tamamsa aktif oluyor; buraya düşülmesi beklenmez, savunma amaçlı.
      setStep("review");
      return undefined;
    }

    const controller = new AbortController();
    setAnalysisError(null);

    submitAnalysisSession({ speech, sustained_vowel: sustainedVowel, glide }, controller.signal)
      .then((result) => {
        setAnalysisResult(result);
        setStep("results");
      })
      .catch((error: unknown) => {
        if (controller.signal.aborted) return;
        setAnalysisError(error instanceof ApiError ? error.message : texts.errors.unexpected);
      });

    return () => controller.abort();
  }, [step, analysisAttempt, recordings]);

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
    setStep(testId);
  }, []);

  const handleAnalyze = useCallback(() => {
    setStep("analyzing");
  }, []);

  const handleRetryAnalysis = useCallback(() => {
    setAnalysisError(null);
    setAnalysisAttempt((previous) => previous + 1);
  }, []);

  const handleBackToReviewFromAnalysis = useCallback(() => {
    setAnalysisError(null);
    setStep("review");
  }, []);

  const handleRestart = useCallback(() => {
    setRecordings((previous) => {
      Object.values(previous).forEach((recording) => {
        if (recording) URL.revokeObjectURL(recording.url);
      });
      return EMPTY_RECORDINGS;
    });
    setAnalysisResult(null);
    setAnalysisError(null);
    setReturnToReview(false);
    setStep("mic-check");
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
    return <RecordingsReview recordings={recordings} onReRecord={handleReRecordFromReview} onAnalyze={handleAnalyze} />;
  }

  if (step === "analyzing") {
    if (analysisError) {
      return (
        <ScreenLayout title={texts.analyzing.title}>
          <p className="analyzing__error" role="alert">
            {analysisError}
          </p>
          <div className="btn-row">
            <button type="button" className="btn btn--primary" onClick={handleRetryAnalysis}>
              {texts.connection.retry}
            </button>
            <button type="button" className="btn btn--secondary" onClick={handleBackToReviewFromAnalysis}>
              {texts.results.backToReview}
            </button>
          </div>
        </ScreenLayout>
      );
    }
    return <AnalyzingScreen />;
  }

  if (step === "results") {
    if (!analysisResult) {
      // Teorik olarak buraya düşülmemeli — "results" adımına yalnızca analiz
      // başarıyla tamamlanınca geçiliyor. Savunma amaçlı geri dönüş ekranı.
      return (
        <ScreenLayout title={texts.results.title}>
          <p role="alert">{texts.errors.unexpected}</p>
          <button type="button" className="btn btn--primary" onClick={() => setStep("review")}>
            {texts.results.backToReview}
          </button>
        </ScreenLayout>
      );
    }
    return (
      <ResultsScreen result={analysisResult} onRestart={handleRestart} onBackToReview={() => setStep("review")} />
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
