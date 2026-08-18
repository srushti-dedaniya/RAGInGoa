import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import SourceCard from "../../src/components/SourceCard/SourceCard";
import AnswerCard from "../../src/components/AnswerCard/AnswerCard";

const source = {
  text: "The best time to visit Palolem is between November and February.",
  chunk_id: "doc-0001-c0",
  metadata: { title: "Palolem Beach Guide", topic: "beaches" },
  score: 0.33,
  score_type: "cosine",
};

describe("SourceCard", () => {
  it("renders title, topic and score", () => {
    render(<SourceCard source={source} index={0} />);
    expect(screen.getByText("Palolem Beach Guide")).toBeInTheDocument();
    expect(screen.getByText("beaches")).toBeInTheDocument();
    expect(screen.getByText(/33%/)).toBeInTheDocument();
  });

  it("renders the chunk text", () => {
    render(<SourceCard source={source} index={1} />);
    expect(screen.getByText(/best time to visit Palolem/)).toBeInTheDocument();
  });
});

describe("AnswerCard", () => {
  const result = {
    answer: "Palolem is best in winter. [Source: Palolem Beach Guide]",
    grounded: true,
    sources: [source],
    latency_breakdown: { retrieval: 1.0, generation: 0.1, guardrails: 1.5, total: 2.6 },
    engine: { stt: "dev", llm: "dev", vector_db: "dev", embedding: "hashing-384" },
    guardrails: { passed: true, checks: [] },
    warnings: [],
  };

  it("renders the grounded answer", () => {
    render(<AnswerCard result={result} />);
    expect(screen.getByText(/Palolem is best in winter/)).toBeInTheDocument();
  });

  it("renders grounding status and latency", () => {
    render(<AnswerCard result={result} />);
    expect(screen.getByText("Grounded")).toBeInTheDocument();
    expect(screen.getByText("1ms")).toBeInTheDocument();
  });

  it("renders nothing without a result", () => {
    const { container } = render(<AnswerCard result={null} />);
    expect(container.firstChild).toBeNull();
  });
});
