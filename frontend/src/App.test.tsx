import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import App from "./App";
import { texts } from "./texts";

function mockFetchOnceOk() {
  return vi.spyOn(globalThis, "fetch").mockResolvedValue(
    new Response(JSON.stringify({ status: "ok", message: "Backend bağlantısı başarılı" }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    }),
  );
}

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
