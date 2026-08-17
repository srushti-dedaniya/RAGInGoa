import { describe, expect, it } from "vitest";
import { formatConfidence, formatLatency } from "../../src/utils/formatLatency";
import { formatDuration, formatTime } from "../../src/utils/formatTime";

describe("formatLatency", () => {
  it("formats milliseconds", () => {
    expect(formatLatency(2)).toBe("2ms");
  });

  it("renders submillisecond values", () => {
    expect(formatLatency(0.4)).toBe("<1ms");
  });

  it("renders seconds for large values", () => {
    expect(formatLatency(2500)).toBe("2.50s");
  });

  it("renders dash for unknown", () => {
    expect(formatLatency(null)).toBe("—");
    expect(formatLatency(undefined)).toBe("—");
  });
});

describe("formatConfidence", () => {
  it("renders percentage", () => {
    expect(formatConfidence(0.818)).toBe("82%");
  });

  it("renders dash for unknown", () => {
    expect(formatConfidence(null)).toBe("—");
  });
});

describe("formatDuration", () => {
  it("formats sub-minute durations", () => {
    expect(formatDuration(42)).toBe("42s");
  });

  it("formats minute/second durations", () => {
    expect(formatDuration(421)).toBe("7m 1s");
  });
});

describe("formatTime", () => {
  it("returns an HH:MM time string", () => {
    const out = formatTime(new Date(2026, 0, 1, 9, 5));
    expect(out).toMatch(/^\d{1,2}:\d{2}(:?\s?am|pm)?$/);
  });
});