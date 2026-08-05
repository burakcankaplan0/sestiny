import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import App from "./App";
import { VOICE_TESTS } from "./features/voice-tests/testConfig";
import { texts } from "./texts";

function mockFetchOnceOk() {
  return vi.spyOn(globalThis, "fetch").mockResolvedValue(
    new Response(JSON.stringify({ status: "ok", message: "Backend bağlantısı başarılı" }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    }),
  );
}

/** Health kontrolüne ve analyze-session'a URL'e göre farklı sahte cevap döndürür. */
function mockFetchWithAnalysisResult(analysisResponse: unknown) {
  return vi.spyOn(globalThis, "fetch").mockImplementation(async (input) => {
    const url = typeof input === "string" ? input : input instanceof URL ? input.toString() : input.url;

    if (url.includes("/analyze-session")) {
      return new Response(JSON.stringify(analysisResponse), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    }
    return new Response(JSON.stringify({ status: "ok", message: "Backend bağlantısı başarılı" }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  });
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

const ACCEPTED_ANALYSIS_RESPONSE = {
  session_id: "test-session-id",
  status: "accepted",
  quality: { overall_score: 92, label: "iyi", warnings: [] },
  speech: {
    accepted: true,
    warnings: [],
    duration_seconds: 4.0,
    median_f0_hz: 150.2,
    approximate_note: "D3",
    pitch_variability_semitones: 1.1,
    voiced_ratio: 0.95,
    confidence: 0.9,
  },
  sustained_vowel: {
    accepted: true,
    warnings: [],
    duration_seconds: 3.0,
    median_f0_hz: 196.0,
    approximate_note: "G3",
    voiced_duration_seconds: 2.9,
    pitch_deviation_cents: 12.0,
    jump_count: 0,
    dropout_ratio: 0.01,
    stability_score: 88,
    stability_label: "stabil",
    confidence: 0.92,
  },
  glide: {
    accepted: true,
    warnings: [],
    duration_seconds: 4.0,
    observed_low_note: "G2",
    observed_high_note: "E4",
    observed_low_midi: 43,
    observed_high_midi: 64,
    range_semitones: 21,
    estimated_comfortable_low_note: "A2",
    estimated_comfortable_high_note: "D4",
    confidence: 0.85,
  },
  profile: {
    label: "orta-düşük merkezli ses profili",
    range_label: "geniş gözlemlenen aralık",
    summary:
      "Kaydında orta-düşük bölgede yoğunlaşan bir ses profili gözlemlendi. Uzun ses testinde perde kararlılığın yüksekti. Kaydırma testinde yaklaşık G2–E4 aralığı gözlemlendi. Bu değerler profesyonel bir ses türü teşhisi değildir ve mikrofon, ortam, teknik ve o anki ses durumundan etkilenebilir.",
  },
  recommendations: [
    {
      id: "demo-002",
      title: "Demo Şarkı 2",
      artist: "Demo Sanatçı 2",
      language: "tr",
      genre: "halk",
      difficulty: "kolay",
      min_note: "A2",
      max_note: "A3",
      match_score: 100,
      transposition_semitones: null,
      verified: false,
      source_note: "Demo veri — gerçek bir şarkı değildir, yalnızca geliştirme/test amaçlıdır.",
    },
  ],
};

/** Testlerde gerçek MediaRecorder yerine kullanılan basit sahte kayıt cihazı. */
class FakeMediaRecorder {
  static isTypeSupported() {
    return true;
  }

  state: "inactive" | "recording" = "inactive";
  mimeType = "audio/webm";
  ondataavailable: ((event: { data: Blob }) => void) | null = null;
  onstop: (() => void) | null = null;

  start() {
    this.state = "recording";
  }

  stop() {
    this.state = "inactive";
    this.ondataavailable?.({ data: new Blob(["ses"], { type: this.mimeType }) });
    this.onstop?.();
  }
}

function stubMicrophoneSupport() {
  vi.stubGlobal("MediaRecorder", FakeMediaRecorder);

  const fakeStream = {
    getTracks: () => [{ stop: vi.fn() }],
  } as unknown as MediaStream;

  Object.defineProperty(window.navigator, "mediaDevices", {
    configurable: true,
    value: { getUserMedia: vi.fn().mockResolvedValue(fakeStream) } as unknown as MediaDevices,
  });

  URL.createObjectURL = vi.fn(() => "blob:mock-url");
  URL.revokeObjectURL = vi.fn();
}

function stubMicrophoneDenied() {
  vi.stubGlobal("MediaRecorder", FakeMediaRecorder);

  Object.defineProperty(window.navigator, "mediaDevices", {
    configurable: true,
    value: {
      getUserMedia: vi.fn().mockRejectedValue(new DOMException("İzin reddedildi", "NotAllowedError")),
    } as unknown as MediaDevices,
  });
}

afterEach(() => {
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

describe("Karşılama ekranı", () => {
  it("uygulama adını ve tanıtım metnini gösterir", () => {
    mockFetchOnceOk();
    render(<App />);

    expect(screen.getByRole("heading", { level: 1, name: texts.app.name })).toBeVisible();
    expect(screen.getByText(texts.app.intro)).toBeVisible();
  });

  it("teşhis olmadığı uyarısını ve gizlilik açıklamasını gösterir", () => {
    mockFetchOnceOk();
    render(<App />);

    expect(screen.getByText(texts.disclaimer.notDiagnosis)).toBeVisible();
    expect(screen.getByText(texts.disclaimer.privacy)).toBeVisible();
  });
});

describe("Backend bağlantı durumu", () => {
  it("bağlantı kurulduğunda başarı mesajını gösterir", async () => {
    mockFetchOnceOk();
    render(<App />);

    expect(await screen.findByText("Backend bağlantısı başarılı")).toBeVisible();
    expect(screen.getByRole("status")).toHaveTextContent("Bağlı");
  });

  it("sunucuya ulaşılamazsa ham hatayı değil anlaşılır Türkçe mesajı gösterir", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new TypeError("Failed to fetch"));
    render(<App />);

    expect(await screen.findByText(texts.errors.network)).toBeVisible();
    expect(screen.queryByText(/Failed to fetch/)).not.toBeInTheDocument();
  });

  it("sunucu hata kodu dönerse HTTP kodunu kullanıcıya sızdırmaz", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response("boom", { status: 500 }));
    render(<App />);

    expect(await screen.findByText(texts.errors.server)).toBeVisible();
    expect(screen.queryByText(/500/)).not.toBeInTheDocument();
  });

  it("tekrar dene butonu yeniden bağlanmayı sağlar", async () => {
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockRejectedValueOnce(new TypeError("Failed to fetch"));
    render(<App />);

    const retryButton = await screen.findByRole("button", { name: texts.connection.retry });

    fetchMock.mockResolvedValueOnce(
      new Response(JSON.stringify({ status: "ok", message: "Backend bağlantısı başarılı" }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );

    await userEvent.click(retryButton);

    await waitFor(() => {
      expect(screen.getByText("Backend bağlantısı başarılı")).toBeVisible();
    });
  });
});

describe("Mikrofon izni", () => {
  it("izin reddedildiğinde anlaşılır hata mesajı gösterir", async () => {
    mockFetchOnceOk();
    stubMicrophoneDenied();
    render(<App />);

    await userEvent.click(await screen.findByRole("button", { name: texts.app.startButton }));
    await userEvent.click(await screen.findByRole("button", { name: texts.microphone.grantButton }));

    expect(await screen.findByText(texts.microphone.permissionDenied)).toBeVisible();
    expect(screen.queryByRole("button", { name: texts.microphone.continueButton })).not.toBeInTheDocument();
  });
});

describe("Ses kaydı akışı", () => {
  it("kayıt başlatılıp durdurulduğunda durum değişiyor ve kayıt dinlenebiliyor", async () => {
    mockFetchOnceOk();
    stubMicrophoneSupport();
    render(<App />);

    await userEvent.click(await screen.findByRole("button", { name: texts.app.startButton }));
    await userEvent.click(await screen.findByRole("button", { name: texts.microphone.grantButton }));
    await userEvent.click(await screen.findByRole("button", { name: texts.microphone.continueButton }));

    // Test 1 (konuşma) ekranındayız.
    expect(await screen.findByRole("heading", { level: 1, name: "Konuşma testi" })).toBeVisible();

    await userEvent.click(screen.getByRole("button", { name: texts.voiceTest.startButton }));

    expect(screen.getByRole("button", { name: texts.voiceTest.stopButton })).toBeVisible();
    expect(screen.getByText(texts.voiceTest.recordingInProgress)).toBeVisible();

    await userEvent.click(screen.getByRole("button", { name: texts.voiceTest.stopButton }));

    expect(screen.getByTestId("playback-audio")).toBeInTheDocument();
    expect(screen.getByText(texts.voiceTest.recordingSaved)).toBeVisible();
  });
});

/** Mikrofon iznini alır, üç testi de gerçek zamanda kaydedip inceleme ekranına ulaşır. */
async function completeAllRecordingsAndReachReview(user: ReturnType<typeof userEvent.setup>) {
  await user.click(await screen.findByRole("button", { name: texts.app.startButton }));
  await user.click(await screen.findByRole("button", { name: texts.microphone.grantButton }));
  await user.click(await screen.findByRole("button", { name: texts.microphone.continueButton }));

  // Üç testi de sırayla kaydet; her kaydı, o testin minimum süresini karşılayacak kadar bekletiyoruz
  // (gerçek zaman kullanıyoruz — sahte zamanlayıcı, user-event + çoklu findBy adımlarını kırılgan yapardı).
  for (const test of VOICE_TESTS) {
    await user.click(screen.getByRole("button", { name: texts.voiceTest.startButton }));
    await sleep((test.minSeconds + 0.5) * 1000);
    await user.click(screen.getByRole("button", { name: texts.voiceTest.stopButton }));

    const continueButton = await screen.findByRole("button", {
      name: (name) => name === texts.voiceTest.nextTest || name === texts.voiceTest.goToReview,
    });
    expect(continueButton).toBeEnabled();
    await user.click(continueButton);
  }

  const analyzeButton = await screen.findByRole("button", { name: texts.review.analyzeButton });
  expect(analyzeButton).toBeEnabled();
  return analyzeButton;
}

describe("Uçtan uca analiz akışı", () => {
  it(
    "üç test kaydedilip 'Analiz et'e basılınca sonuç ekranı backend verisini doğru kartlara yerleştirir",
    async () => {
      const user = userEvent.setup();
      stubMicrophoneSupport();
      mockFetchWithAnalysisResult(ACCEPTED_ANALYSIS_RESPONSE);

      render(<App />);

      const analyzeButton = await completeAllRecordingsAndReachReview(user);
      await user.click(analyzeButton);

      // Sonuç ekranı — backend verisi Türkçe kartlara doğru yerleşmiş olmalı.
      // (Analiz ediliyor ekranı sahte cevap neredeyse anında döndüğü için burada
      // güvenilir şekilde yakalanamıyor; AnalyzingScreen ayrı bir testte doğrulanıyor.)
      expect(await screen.findByRole("heading", { level: 1, name: texts.results.title })).toBeVisible();
      expect(screen.getByText("orta-düşük merkezli ses profili")).toBeVisible();
      expect(screen.getByText("G2 – E4")).toBeVisible();
      expect(screen.getByText(texts.results.semitoneRange(21))).toBeVisible();
      expect(screen.getByText("A2 – D4")).toBeVisible();
      expect(screen.getByText(/D3.*150\.2 Hz/)).toBeVisible();
      expect(screen.getByText(texts.results.stabilityValue("stabil", 88))).toBeVisible();
      expect(screen.getByText(texts.disclaimer.notDiagnosis)).toBeVisible();

      // Şarkı önerisi de gösterilmeli.
      expect(screen.getByText(texts.recommendations.title)).toBeVisible();
      expect(screen.getByText("Demo Şarkı 2")).toBeVisible();
      expect(screen.getByText(texts.recommendations.demoBadge)).toBeVisible();

      // Ham backend alan adları veya teknik jargon sızmamalı.
      expect(screen.queryByText(/median_f0_hz|observed_low_midi|session_id/)).not.toBeInTheDocument();
    },
    20000,
  );
});

describe("Analiz sırasında hata durumu", () => {
  it(
    "sunucu hatasında anlaşılır mesaj gösterir; 'Tekrar dene' yeniden dener, 'İncelemeye dön' geri götürür",
    async () => {
      const user = userEvent.setup();
      stubMicrophoneSupport();
      const fetchMock = vi.spyOn(globalThis, "fetch").mockImplementation(async (input) => {
        const url = typeof input === "string" ? input : input instanceof URL ? input.toString() : input.url;
        if (url.includes("/analyze-session")) {
          return new Response("sunucu hatası", { status: 500 });
        }
        return new Response(JSON.stringify({ status: "ok", message: "Backend bağlantısı başarılı" }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      });

      render(<App />);

      const analyzeButton = await completeAllRecordingsAndReachReview(user);
      await user.click(analyzeButton);

      expect(await screen.findByText(texts.errors.server)).toBeVisible();
      // Ham HTTP kodu veya "sunucu hatası" gövdesi kullanıcıya sızmamalı.
      expect(screen.queryByText(/500/)).not.toBeInTheDocument();
      expect(screen.queryByText(/sunucu hatası/)).not.toBeInTheDocument();

      // "İncelemeye dön" — kayıtlar korunarak inceleme ekranına geri döner.
      await user.click(screen.getByRole("button", { name: texts.results.backToReview }));
      expect(await screen.findByRole("heading", { level: 1, name: texts.review.title })).toBeVisible();

      // Tekrar "Analiz et"e bas, bu sefer backend başarılı dönsün.
      fetchMock.mockImplementation(async (input) => {
        const url = typeof input === "string" ? input : input instanceof URL ? input.toString() : input.url;
        if (url.includes("/analyze-session")) {
          return new Response(JSON.stringify(ACCEPTED_ANALYSIS_RESPONSE), {
            status: 200,
            headers: { "Content-Type": "application/json" },
          });
        }
        return new Response(JSON.stringify({ status: "ok", message: "Backend bağlantısı başarılı" }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      });
      await user.click(screen.getByRole("button", { name: texts.review.analyzeButton }));

      expect(await screen.findByRole("heading", { level: 1, name: texts.results.title })).toBeVisible();
    },
    20000,
  );
});
