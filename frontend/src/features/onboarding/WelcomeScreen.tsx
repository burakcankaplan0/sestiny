import { ConnectionStatus } from "../../components/ConnectionStatus";
import { ScreenLayout } from "../../components/ScreenLayout";
import { texts } from "../../texts";
import type { HealthStatus } from "../../hooks/useBackendHealth";
import "../../App.css";

interface WelcomeScreenProps {
  healthStatus: HealthStatus;
  healthMessage: string;
  onRetryHealth: () => void;
  onStart: () => void;
}

export function WelcomeScreen({ healthStatus, healthMessage, onRetryHealth, onStart }: WelcomeScreenProps) {
  return (
    <ScreenLayout eyebrow={texts.app.tagline} title={texts.app.name} description={texts.app.intro}>
      <ConnectionStatus status={healthStatus} message={healthMessage} onRetry={onRetryHealth} />

      <section className="notice" aria-labelledby="notice-title">
        <h2 className="notice__title" id="notice-title">
          {texts.disclaimer.title}
        </h2>
        <p className="notice__text">{texts.disclaimer.notDiagnosis}</p>
        <p className="notice__text">{texts.disclaimer.privacy}</p>
      </section>

      <button type="button" className="btn btn--primary" onClick={onStart}>
        {texts.app.startButton}
      </button>
    </ScreenLayout>
  );
}
