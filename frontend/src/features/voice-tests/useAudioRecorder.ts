import { useCallback, useEffect, useRef, useState } from "react";

import type { RecordingResult } from "../../types/recording";

/** Tarayıcının desteklediği ilk uygun ses formatı seçilir; sırayla denenir. */
const CANDIDATE_MIME_TYPES = [
  "audio/webm;codecs=opus",
  "audio/webm",
  "audio/mp4",
  "audio/ogg;codecs=opus",
];

/** Süre sayacının güncellenme sıklığı. Daha sık güncellemek gözle fark edilmez, gereksiz render üretir. */
const TIMER_TICK_MS = 100;

function pickSupportedMimeType(): string | undefined {
  if (typeof MediaRecorder === "undefined" || !MediaRecorder.isTypeSupported) {
    return undefined;
  }
  return CANDIDATE_MIME_TYPES.find((type) => MediaRecorder.isTypeSupported(type));
}

export type RecorderPhase = "idle" | "recording";

interface UseAudioRecorderResult {
  phase: RecorderPhase;
  elapsedSeconds: number;
  start: () => void;
  stop: () => void;
}

/**
 * Tek bir ses testi için kayıt makinesi.
 * Kayıt bitince (elle durdurulsun veya maxSeconds'a ulaşılsın) onComplete çağrılır
 * ve makine otomatik olarak idle durumuna döner — sonucu kalıcı tutmak çağıranın işi.
 */
export function useAudioRecorder(
  stream: MediaStream | null,
  maxSeconds: number,
  onComplete: (result: RecordingResult) => void,
): UseAudioRecorderResult {
  const [phase, setPhase] = useState<RecorderPhase>("idle");
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const startedAtRef = useRef(0);
  const intervalRef = useRef<number | null>(null);
  const onCompleteRef = useRef(onComplete);
  onCompleteRef.current = onComplete;

  const clearTimer = useCallback(() => {
    if (intervalRef.current !== null) {
      window.clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  const stop = useCallback(() => {
    const recorder = recorderRef.current;
    if (recorder && recorder.state !== "inactive") {
      recorder.stop();
    }
  }, []);

  const start = useCallback(() => {
    // Aynı anda yalnızca bir kayıt yapılabilsin: zaten kayıttaysa yeni bir tane başlatma.
    if (!stream || phase === "recording") return;

    const mimeType = pickSupportedMimeType();
    const recorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);
    chunksRef.current = [];

    recorder.ondataavailable = (event) => {
      if (event.data.size > 0) chunksRef.current.push(event.data);
    };

    recorder.onstop = () => {
      clearTimer();
      const blob = new Blob(chunksRef.current, { type: recorder.mimeType || mimeType || "audio/webm" });
      const url = URL.createObjectURL(blob);
      const durationSeconds = (Date.now() - startedAtRef.current) / 1000;
      setPhase("idle");
      setElapsedSeconds(0);
      onCompleteRef.current({ blob, mimeType: blob.type, url, durationSeconds });
    };

    recorderRef.current = recorder;
    startedAtRef.current = Date.now();
    setElapsedSeconds(0);
    setPhase("recording");
    recorder.start();

    intervalRef.current = window.setInterval(() => {
      const seconds = (Date.now() - startedAtRef.current) / 1000;
      setElapsedSeconds(seconds);
      if (seconds >= maxSeconds) {
        stop();
      }
    }, TIMER_TICK_MS);
  }, [stream, phase, maxSeconds, stop, clearTimer]);

  // Bileşen kaldırılırsa aktif kaydı ve zamanlayıcıyı temizle.
  useEffect(() => {
    return () => {
      clearTimer();
      if (recorderRef.current && recorderRef.current.state !== "inactive") {
        recorderRef.current.stop();
      }
    };
  }, [clearTimer]);

  return { phase, elapsedSeconds, start, stop };
}
