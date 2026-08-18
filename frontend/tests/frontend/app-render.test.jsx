import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import App from "../../src/App";

describe("App smoke render", () => {
  it("renders the RAGInGoa shell without throwing", () => {
    const { container } = render(<App />);
    expect(container.textContent).toMatch(/RAGInGoa|HH GOA 2026/);
    expect(screen.getAllByRole("button", { name: "Start recording" })).toHaveLength(1);
    expect(screen.getByRole("button", { name: "English" })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByRole("button", { name: "हिन्दी" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "मराठी" })).toBeInTheDocument();
  });
});
