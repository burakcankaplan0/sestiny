import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { RecordingsReview } from "./RecordingsReview";
import { texts } from "../../texts";
import type { RecordingResult, RecordingsState } from "../../types/recording";

function makeRecording(): RecordingResult {
  return {
    blob: new Blob(["ses"], { type: "audio/webm" }),
    mimeType: "audio/webm",
    url: "blob:mock-url",
    durationSeconds: 6,
  };
}

const EMPTY: RecordingsState = { speech: null, sustained_vowel: null, glide: null };

describe("RecordingsReview", () => {
  it("üç kayıt tamamlanmadan analiz butonunu pasif tutar", () => {
    render(
      <RecordingsReview
        recordings={{ ...EMPTY, speech: makeRecording() }}
        onReRecord={vi.fn()}
        onAnalyze={vi.fn()}
      />,
    );

    expect(screen.getByRole("button", { name: texts.review.analyzeButton })).toBeDisabled();
    expect(screen.getByText(texts.review.analyzeDisabledHint)).toBeVisible();
  });

  it("üç kayıt tamamlanınca analiz butonunu aktif eder", () => {
    render(
      <RecordingsReview
        recordings={{ speech: makeRecording(), sustained_vowel: makeRecording(), glide: makeRecording() }}
        onReRecord={vi.fn()}
        onAnalyze={vi.fn()}
      />,
    );

    expect(screen.getByRole("button", { name: texts.review.analyzeButton })).toBeEnabled();
    expect(screen.queryByText(texts.review.analyzeDisabledHint)).not.toBeInTheDocument();
  });
});
