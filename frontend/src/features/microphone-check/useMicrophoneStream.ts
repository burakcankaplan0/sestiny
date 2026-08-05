import { useCallback, useEffect, useRef, useState } from "react";

import { texts } from "../../texts";

export type MicrophoneStatus = "idle" | "requesting" | "granted" | "denied" | "unsupported";

interface UseMicrophoneStreamResult {
  status: MicrophoneStatus;
  errorMessage: string | null;
  stream: MediaStream | null;
  isSupported: boolean;
  requestAccess: () => Promise<void>;
}

function isBrowserSupported(): boolean {
  return (
    typeof navigator !== "undefined" &&
    typeof navigator.mediaDevices?.getUserMedia === "function" &&
    typeof window.MediaRecorder !== "undefined"
  );
}

/** getUserMedia'nın DOMException isimlerini anlaşılır Türkçe mesajlara çevirir. */
function describeMicrophoneError(error: unknown): string {
  if (error instanceof DOMException) {
    switch (error.name) {
      case "NotAllowedError":
      case "PermissionDeniedError":
        return texts.microphone.permissionDenied;
      case "NotFoundError":
      case "DevicesNotFoundError":
        return texts.microphone.noDevice;
      case "NotReadableError":
      case "TrackStartError":
        return texts.microphone.deviceBusy;
      default:
        return texts.microphone.genericError;
    }
  }
  return texts.microphone.genericError;
}

/** Mikrofon iznini ister ve elde edilen MediaStream'i oturum boyunca canlı tutar. */
export function useMicrophoneStream(): UseMicrophoneStreamResult {
  const [status, setStatus] = useState<MicrophoneStatus>("idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const isSupported = isBrowserSupported();

  const requestAccess = useCallback(async () => {
    if (!isSupported) {
      setStatus("unsupported");
      setErrorMessage(texts.microphone.unsupported);
      return;
    }

    setStatus("requesting");
    setErrorMessage(null);

    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = mediaStream;
      setStream(mediaStream);
      setStatus("granted");
    } catch (error) {
      setStatus("denied");
      setErrorMessage(describeMicrophoneError(error));
    }
  }, [isSupported]);

  // Sayfa/uygulama kapanırken mikrofon LED'inin sönmesi için akışı kapat.
  useEffect(() => {
    return () => {
      streamRef.current?.getTracks().forEach((track) => track.stop());
    };
  }, []);

  return { status, errorMessage, stream, isSupported, requestAccess };
}
