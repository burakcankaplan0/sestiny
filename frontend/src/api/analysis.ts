import { apiPostForm } from "./client";
import type { AnalyzeSessionResponse } from "../types/analysis";
import type { RecordingsState } from "../types/recording";

function fileExtensionForMimeType(mimeType: string): string {
  const subtype = mimeType.split(";")[0]?.split("/")[1];
  return subtype || "webm";
}

/** Üç kaydı tek bir multipart isteğinde backend'e gönderir. Çağıran, üçünün de dolu olduğunu garanti eder. */
export function submitAnalysisSession(
  recordings: RecordingsState,
  signal?: AbortSignal,
): Promise<AnalyzeSessionResponse> {
  const form = new FormData();

  (Object.entries(recordings) as [keyof RecordingsState, RecordingsState[keyof RecordingsState]][]).forEach(
    ([testId, recording]) => {
      if (!recording) return;
      const filename = `${testId}.${fileExtensionForMimeType(recording.mimeType)}`;
      form.append(testId, recording.blob, filename);
    },
  );

  return apiPostForm<AnalyzeSessionResponse>("/analyze-session", form, signal);
}
