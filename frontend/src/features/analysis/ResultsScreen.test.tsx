import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { ResultsScreen } from "./ResultsScreen";
import { texts } from "../../texts";
import type { AnalyzeSessionResponse, SongRecommendation } from "../../types/analysis";

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

function makeRecommendation(overrides: Partial<SongRecommendation> = {}): SongRecommendation {
  return {
    id: "demo-001",
    title: "Demo Şarkı 1",
    artist: "Demo Sanatçı 1",
    language: "tr",
    genre: "pop",
    difficulty: "kolay",
    min_note: "A2",
    max_note: "A3",
    match_score: 90,
    transposition_semitones: null,
    verified: false,
    source_note: "Demo veri — gerçek bir şarkı değildir.",
    freely_transposable: false,
    ...overrides,
  };
}

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
    recommendations: [],
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

describe("ResultsScreen — şarkı önerileri", () => {
  it("öneri yoksa kart listesi yerine nedenini açıklayan bir not gösterir", () => {
    render(<ResultsScreen result={baseResult({ recommendations: [] })} onRestart={vi.fn()} onBackToReview={vi.fn()} />);

    expect(screen.queryByText(texts.recommendations.title)).not.toBeInTheDocument();
    expect(screen.getByText(texts.results.recommendationsUnavailableTitle)).toBeVisible();
    expect(screen.getByText(texts.results.recommendationsUnavailableText)).toBeVisible();
  });

  it("öneri kartları başlık, sanatçı, tür, zorluk, aralık ve eşleşme yüzdesini gösterir", () => {
    const recommendations = [makeRecommendation({ match_score: 82 })];
    render(
      <ResultsScreen result={baseResult({ recommendations })} onRestart={vi.fn()} onBackToReview={vi.fn()} />,
    );

    expect(screen.getByText(texts.recommendations.title)).toBeVisible();
    expect(screen.getByText("Demo Şarkı 1")).toBeVisible();
    expect(screen.getByText("Demo Sanatçı 1")).toBeVisible();
    expect(screen.getByText(texts.recommendations.matchLabel(82))).toBeVisible();
    expect(screen.getByText(texts.recommendations.rangeLabel("A2", "A3"))).toBeVisible();
  });

  it("doğrulanmamış (demo) şarkılarda 'Demo veri' rozeti gösterir", () => {
    const recommendations = [makeRecommendation({ verified: false })];
    render(
      <ResultsScreen result={baseResult({ recommendations })} onRestart={vi.fn()} onBackToReview={vi.fn()} />,
    );

    expect(screen.getByText(texts.recommendations.demoBadge)).toBeVisible();
  });

  it("negatif transposition_semitones 'aşağıdan' ipucu gösterir", () => {
    const recommendations = [makeRecommendation({ transposition_semitones: -2 })];
    render(
      <ResultsScreen result={baseResult({ recommendations })} onRestart={vi.fn()} onBackToReview={vi.fn()} />,
    );

    expect(screen.getByText(texts.recommendations.transposeDown(2))).toBeVisible();
  });

  it("pozitif transposition_semitones 'yukarıdan' ipucu gösterir", () => {
    const recommendations = [makeRecommendation({ transposition_semitones: 3 })];
    render(
      <ResultsScreen result={baseResult({ recommendations })} onRestart={vi.fn()} onBackToReview={vi.fn()} />,
    );

    expect(screen.getByText(texts.recommendations.transposeUp(3))).toBeVisible();
  });

  it("serbest transpoze edilebilen eserde sayısal yarı ton yerine açıklama gösterir", () => {
    // Makam müziğinde hesaplanan kaydırma 20-30 yarı tona çıkabiliyor; kullanıcıya
    // bu sayıyı göstermek anlamsız olurdu (bkz. K-060).
    const recommendations = [
      makeRecommendation({ freely_transposable: true, transposition_semitones: -29 }),
    ];
    render(
      <ResultsScreen result={baseResult({ recommendations })} onRestart={vi.fn()} onBackToReview={vi.fn()} />,
    );

    expect(screen.getByText(texts.recommendations.singableInAnyKey)).toBeVisible();
    expect(screen.queryByText(/29 semiton/)).not.toBeInTheDocument();
  });

  it("zorluk filtresi yalnızca seçilen zorluktaki şarkıları gösterir", async () => {
    const user = userEvent.setup();
    const recommendations = [
      makeRecommendation({ id: "a", title: "Demo Şarkı A", difficulty: "kolay" }),
      makeRecommendation({ id: "b", title: "Demo Şarkı B", difficulty: "zor" }),
    ];
    render(
      <ResultsScreen result={baseResult({ recommendations })} onRestart={vi.fn()} onBackToReview={vi.fn()} />,
    );

    expect(screen.getByText("Demo Şarkı A")).toBeVisible();
    expect(screen.getByText("Demo Şarkı B")).toBeVisible();

    await user.click(screen.getByRole("button", { name: texts.recommendations.difficultyHard }));

    expect(screen.queryByText("Demo Şarkı A")).not.toBeInTheDocument();
    expect(screen.getByText("Demo Şarkı B")).toBeVisible();
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
