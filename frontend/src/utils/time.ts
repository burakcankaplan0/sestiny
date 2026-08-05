const SECONDS_PER_MINUTE = 60;

/** Saniyeyi "dakika:saniye" biçimine çevirir. Negatif veya kesirli girdilerde 0'a yuvarlar. */
export function formatSeconds(totalSeconds: number): string {
  const safeSeconds = Math.max(0, Math.floor(totalSeconds));
  const minutes = Math.floor(safeSeconds / SECONDS_PER_MINUTE);
  const seconds = safeSeconds % SECONDS_PER_MINUTE;
  return `${minutes}:${seconds.toString().padStart(2, "0")}`;
}
