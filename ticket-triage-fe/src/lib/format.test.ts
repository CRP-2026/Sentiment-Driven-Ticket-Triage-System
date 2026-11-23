import { describe, expect, it } from "vitest";
import { formatDate, formatScore } from "./format";

describe("format utilities", () => {
  it("formats score to 1 decimal place", () => {
    expect(formatScore(85.67)).toBe("85.7");
    expect(formatScore(10)).toBe("10.0");
    expect(formatScore(0)).toBe("0.0");
  });

  it("formats valid date string", () => {
    const result = formatDate("2026-10-24T00:00:00Z");
    expect(typeof result).toBe("string");
    expect(result.length).toBeGreaterThan(0);
  });

  it("handles fallback gracefully", () => {
    // If invalid date is passed, check it doesn't throw
    expect(typeof formatDate("invalid-date")).toBe("string");
  });
});
