import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { RAGProvider } from "../../src/context/RAGContext";
import Ask from "../../src/pages/Ask/Ask";

describe("Ask page", () => {
  it("renders the RAG interface with the original mic circle", () => {
    render(
      <RAGProvider>
        <MemoryRouter>
          <Ask />
        </MemoryRouter>
      </RAGProvider>
    );
    expect(screen.getByText("Back to Home")).toBeInTheDocument();
    expect(screen.getByLabelText("Record your question")).toBeInTheDocument();
    expect(screen.getByText("Query Workspace")).toBeInTheDocument();
    expect(screen.getByText("Grounded. Or nothing.")).toBeInTheDocument();
    expect(screen.getByText("Latency. Measured.")).toBeInTheDocument();
    expect(screen.getByText("DEV BENCHMARK · P50 / P95 / P99 · REPRODUCIBLE")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Run benchmark" })).toBeInTheDocument();
  });
});