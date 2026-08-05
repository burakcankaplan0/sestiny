import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { AnalyzingScreen } from "./AnalyzingScreen";
import { texts } from "../../texts";

describe("AnalyzingScreen", () => {
  it("başlığı ve ilk aşama mesajını gösterir; sahte yüzde göstergesi yok", () => {
    render(<AnalyzingScreen />);

    expect(screen.getByRole("heading", { level: 1, name: texts.analyzing.title })).toBeVisible();
    expect(screen.getByText(texts.analyzing.stage1)).toBeVisible();
    expect(screen.queryByText(/%\d/)).not.toBeInTheDocument();
  });
});
