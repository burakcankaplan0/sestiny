import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { ResultsScreen } from "./ResultsScreen";
import { texts } from "../../texts";
import type { AnalyzeSessionResponse } from "../../types/analysis";

const FORBIDDEN_PHRASES = [
  "kesin",
  "sağlıklı",
  "sağlıksız",
  "teşhis konuldu",
  "bariton",
  "tenor",
  "soprano",
  "alto",
];

function baseResult(overrides: Partial<AnalyzeSessionResponse> = {}): AnalyzeSessionResponse {
  return {
    session_id: "test-session",
    status: "accepted",
    quality: { overall_score: 90, label: "iyi", warnings: [] },
    speech: {
      accepted: true,
      warnings: [],
      duration_seconds: 4,
      median_f0_hz: 150.2,
      approximate_note: "D3",
      pitch_variability_semitones: 1.1,
      voiced_ratio: 0.9,
      confidence: 0.9,
    },
    sustained_vowel: {
      accepted: true,
      warnings: [],
      duration_seconds: 3,
      median_f0_hz: 196.0,
      approximate_note: "G3",
      voiced_duration_seconds: 2.9,
      pitch_deviation_cents: 10,
      jump_count: 0,
      dropout_ratio: 0.01,
      stability_score: 85,
      stability_label: "stabil",
      confidence: 0.9,
    },
    glide: {
      accepted: true,
      warnings: [],
      duration_seconds: 4,
      observed_low_note: "G2",
      observed_high_note: "E4",
      observed_low_midi: 43,
      observed_high_midi: 64,
      range_semitones: 21,
      estimated_comfortable_low_note: "A2",
      estimated_comfortable_high_note: "D4",
      confidence: 0.9,
    },
    profile: {
      label: "orta-düşük merkezli ses profili",
      range_label: "geniş gözlemlenen aralık",
      summary:
        "Kaydında orta-düşük bölgede yoğunlaşan bir ses profili gözlemlendi. Bu değerler profesyonel bir ses türü teşhisi değildir.",
    },
    ...overrides,
  };
}

describe("ResultsScreen — kabul edilen oturum", () => {
  it("backend verisini doğru Türkçe kartlara yerleştirir", () => {
    render(<ResultsScreen result={baseResult()} onRestart={vi.fn()} onBackToReview={vi.fn()} />);

    expect(screen.getByRole("heading", { level: 1, name: texts.results.title })).toBeVisible();
    expect(screen.getByText("orta-düşük merkezli ses profili")).toBeVisible();
    expect(screen.getByText("G2 – E4")).toBeVisible();
    expect(screen.getByText(texts.results.semitoneRange(21))).toBeVisible();
    expect(screen.getByText("A2 – D4")).toBeVisible();
    expect(screen.getByText(texts.results.stabilityValue("stabil", 85))).toBeVisible();
    expect(screen.getByText(texts.results.secondsValue(2.9))).toBeVisible();
    expect(screen.getByText("iyi")).toBeVisible();
    expect(screen.getByText(texts.disclaimer.notDiagnosis)).toBeVisible();
  });

  it("profil belirlenemediyse uydurma profil göstermez", () => {
    render(<ResultsScreen result={baseResult({ profile: null })} onRestart={vi.fn()} onBackToReview={vi.fn()} />);

    expect(screen.getByText(texts.results.profileUnavailable)).toBeVisible();
  });

  it("glide aralığı belirlenemediyse uydurma nota göstermez", () => {
    const result = baseResult({
      glide: {
        accepted: true,
        warnings: [],
        duration_seconds: 4,
        observed_low_note: null,
        observed_high_note: null,
        observed_low_midi: null,
        observed_high_midi: null,
        range_semitones: null,
        estimated_comfortable_low_note: null,
        estimated_comfortable_high_note: null,
        confidence: 0.1,
      },
      profile: null,
    });
    render(<ResultsScreen result={result} onRestart={vi.fn()} onBackToReview={vi.fn()} />);

    expect(screen.getAllByText(texts.results.unavailable).length).toBeGreaterThan(0);
    expect(screen.queryByText("G2 – E4")).not.toBeInTheDocument();
  });

  it("düşük güven skorunda temkinli-ol notu gösterir", () => {
    const result = baseResult({
      glide: { ...baseResult().glide, confidence: 0.2 },
    });
    render(<ResultsScreen result={result} onRestart={vi.fn()} onBackToReview={vi.fn()} />);

    expect(screen.getAllByText(texts.results.lowConfidenceNote).length).toBeGreaterThan(0);
  });

  it("yüksek güven skorunda temkinli-ol notu göstermez", () => {
    render(<ResultsScreen result={baseResult()} onRestart={vi.fn()} onBackToReview={vi.fn()} />);

    expect(screen.queryByText(texts.results.lowConfidenceNote)).not.toBeInTheDocument();
  });

  it("hiçbir yerde kesin/tıbbi ifade veya klasik ses türü adı geçmez", () => {
    render(<ResultsScreen result={baseResult()} onRestart={vi.fn()} onBackToReview={vi.fn()} />);

    const bodyText = document.body.textContent?.toLowerCase() ?? "";
    for (const forbidden of FORBIDDEN_PHRASES) {
      expect(bodyText).not.toContain(forbidden);
    }
  });

  it("'Testi yeniden yap' butonu onRestart'ı tetikler", async () => {
    const user = userEvent.setup();
    const onRestart = vi.fn();
    render(<ResultsScreen result={baseResult()} onRestart={onRestart} onBackToReview={vi.fn()} />);

    await user.click(screen.getByRole("button", { name: texts.results.redoAll }));

    expect(onRestart).toHaveBeenCalledOnce();
  });
});

describe("ResultsScreen — reddedilen oturum", () => {
  it("veri kartları yerine uyarıları ve incelemeye dön butonunu gösterir", async () => {
    const user = userEvent.setup();
    const onBackToReview = vi.fn();
    const result = baseResult({
      status: "rejected",
      quality: {
        overall_score: 20,
        label: "yetersiz",
        warnings: ["Konuşma testi: Kayıt çok kısa görünüyor."],
      },
    });

    render(<ResultsScreen result={result} onRestart={vi.fn()} onBackToReview={onBackToReview} />);

    expect(screen.getByRole("heading", { level: 1, name: texts.results.rejectedTitle })).toBeVisible();
    expect(screen.getByText("Konuşma testi: Kayıt çok kısa görünüyor.")).toBeVisible();
    expect(screen.queryByText(texts.results.title)).not.toBeInTheDocument();
    expect(screen.queryByText("G2 – E4")).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: texts.results.backToReview }));
    expect(onBackToReview).toHaveBeenCalledOnce();
  });
});
