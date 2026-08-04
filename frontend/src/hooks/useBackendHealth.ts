import { useCallback, useEffect, useState } from "react";

import { fetchHealth } from "../api/health";
import { ApiError } from "../api/client";
import { texts } from "../texts";

export type HealthStatus = "checking" | "connected" | "error";

interface UseBackendHealthResult {
  status: HealthStatus;
  message: string;
  retry: () => void;
}

/** Backend'e ulaşılabildiğini kontrol eder ve durumu döndürür. */
export function useBackendHealth(): UseBackendHealthResult {
  const [status, setStatus] = useState<HealthStatus>("checking");
  const [message, setMessage] = useState<string>(texts.connection.checking);
  // Değişmesi yeniden kontrol tetikler; retry() bunu artırır.
  const [attempt, setAttempt] = useState(0);

  const retry = useCallback(() => setAttempt((value) => value + 1), []);

  useEffect(() => {
    const controller = new AbortController();

    setStatus("checking");
    setMessage(texts.connection.checking);

    fetchHealth(controller.signal)
      .then((result) => {
        setStatus("connected");
        setMessage(result.message);
      })
      .catch((error: unknown) => {
        // Bileşen sökülürken iptal edilen istek gerçek bir hata değil.
        if (controller.signal.aborted) return;

        setStatus("error");
        setMessage(error instanceof ApiError ? error.message : texts.errors.unexpected);
      });

    return () => controller.abort();
  }, [attempt]);

  return { status, message, retry };
}
