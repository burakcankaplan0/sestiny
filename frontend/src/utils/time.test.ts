import { describe, expect, it } from "vitest";

import { formatSeconds } from "./time";

describe("formatSeconds", () => {
  it("bir dakikanın altındaki saniyeleri biçimlendirir", () => {
    expect(formatSeconds(7)).toBe("0:07");
  });

  it("dakika ve saniyeyi birlikte gösterir", () => {
    expect(formatSeconds(125)).toBe("2:05");
  });

  it("kesirli saniyeleri aşağı yuvarlar", () => {
    expect(formatSeconds(59.9)).toBe("0:59");
  });

  it("negatif değerde 0:00 döndürür", () => {
    expect(formatSeconds(-3)).toBe("0:00");
  });
});
