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

afterEach(() => {
  vi.restoreAllMocks();
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
