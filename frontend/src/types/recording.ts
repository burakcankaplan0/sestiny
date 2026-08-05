/** Tek bir ses testi kaydının bellekteki hâli. Backend'e gönderilene kadar diskte durmaz. */
export interface RecordingResult {
  blob: Blob;
  mimeType: string;
  /** Oynatma için oluşturulan geçici tarayıcı URL'i (URL.createObjectURL). */
  url: string;
  durationSeconds: number;
}

/** Üç zorunlu test. Alan adları backend'e gönderilecek multipart alan adlarıyla aynı tutulur. */
export type TestId = "speech" | "sustained_vowel" | "glide";

export type RecordingsState = Record<TestId, RecordingResult | null>;
