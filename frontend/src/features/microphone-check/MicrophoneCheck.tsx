import { ScreenLayout } from "../../components/ScreenLayout";
import { texts } from "../../texts";
import { useMicrophoneLevel } from "./useMicrophoneLevel";
import type { MicrophoneStatus } from "./useMicrophoneStream";
import "./MicrophoneCheck.css";

interface MicrophoneCheckProps {
  status: MicrophoneStatus;
  errorMessage: string | null;
  isSupported: boolean;
  stream: MediaStream | null;
  onRequestAccess: () => void;
  onContinue: () => void;
}

/** Ses seviyesi çubuğunun "mikrofon algılıyor" sayılması için eşik. Görsel geri bildirim amaçlıdır. */
const LEVEL_ACTIVE_THRESHOLD = 0.05;

export function MicrophoneCheck({
  status,
  errorMessage,
  isSupported,
  stream,
  onRequestAccess,
  onContinue,
}: MicrophoneCheckProps) {
  const level = useMicrophoneLevel(stream);
  const isGranted = status === "granted";

  return (
    <ScreenLayout title={texts.microphone.title} description={texts.microphone.intro}>
      <p className="mic-check__tip">{texts.microphone.environmentTip}</p>

      {!isGranted && (
        <div className="mic-check__action">
          <button
            type="button"
            className="btn btn--primary"
            onClick={onRequestAccess}
            disabled={status === "requesting" || !isSupported}
          >
            {status === "requesting" ? texts.microphone.requesting : texts.microphone.grantButton}
          </button>

          {errorMessage && (
            <p className="mic-check__error" role="alert">
              {errorMessage}
            </p>
          )}

          {status === "denied" && (
            <button type="button" className="btn btn--secondary" onClick={onRequestAccess}>
              {texts.microphone.retryButton}
            </button>
          )}
        </div>
      )}

      {isGranted && (
        <div className="mic-check__level">
          <div className="mic-check__level-bar" aria-hidden="true">
            <div className="mic-check__level-fill" style={{ width: `${Math.round(level * 100)}%` }} />
          </div>
          <p className="mic-check__level-hint" role="status" aria-live="polite">
            {level > LEVEL_ACTIVE_THRESHOLD ? texts.microphone.levelActiveHint : texts.microphone.levelIdleHint}
          </p>

          <button type="button" className="btn btn--primary" onClick={onContinue}>
            {texts.microphone.continueButton}
          </button>
        </div>
      )}
    </ScreenLayout>
  );
}
