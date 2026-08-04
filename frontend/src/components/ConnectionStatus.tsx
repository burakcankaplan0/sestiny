import { texts } from "../texts";
import type { HealthStatus } from "../hooks/useBackendHealth";
import "./ConnectionStatus.css";

interface ConnectionStatusProps {
  status: HealthStatus;
  message: string;
  onRetry: () => void;
}

/**
 * Backend bağlantı durumunu gösterir.
 *
 * Durum yalnızca renkle değil, ayrı bir metin etiketiyle de anlatılır;
 * renk körlüğü olan ve ekran okuyucu kullanan kişiler için gerekli.
 */
export function ConnectionStatus({ status, message, onRetry }: ConnectionStatusProps) {
  const stateLabel: Record<HealthStatus, string> = {
    checking: "Kontrol ediliyor",
    connected: "Bağlı",
    error: "Bağlanamadı",
  };

  return (
    <div className={`connection connection--${status}`} role="status" aria-live="polite">
      <div className="connection__row">
        <span className="connection__dot" aria-hidden="true" />
        <span className="connection__label">
          {texts.connection.label}: {stateLabel[status]}
        </span>
      </div>

      <p className="connection__message">{message}</p>

      {status === "error" && (
        <button type="button" className="connection__retry" onClick={onRetry}>
          {texts.connection.retry}
        </button>
      )}
    </div>
  );
}
