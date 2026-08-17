import { describe, expect, it } from "vitest";
import { render } from "@testing-library/react";
import App from "../../src/App";

describe("App smoke render", () => {
  it("renders the RAGInGoa shell without throwing", () => {
    const { container } = render(<App />);
    expect(container.textContent).toMatch(/RAGInGoa|HH GOA 2026/);
  });
});