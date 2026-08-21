import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import Destinations from "../../src/pages/Destinations/Destinations";
import About from "../../src/pages/About/About";

describe("Destinations page", () => {
  it("renders the destinations page with cards and nav", () => {
    render(
      <MemoryRouter>
        <Destinations />
      </MemoryRouter>
    );
    expect(screen.getByText("Explore Goa")).toBeInTheDocument();
    expect(screen.getByText("Palolem")).toBeInTheDocument();
    expect(screen.getByText("Anjuna")).toBeInTheDocument();
    expect(screen.getByText("Baga")).toBeInTheDocument();
    expect(screen.getByText("Panaji")).toBeInTheDocument();
    expect(screen.getByText("Old Goa")).toBeInTheDocument();
    expect(screen.getByText("Morjim")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Destinations" })).toHaveAttribute("href", "/destinations");
    expect(screen.getByRole("link", { name: "Ask" })).toHaveAttribute("href", "/ask");
  });
});

describe("About page", () => {
  it("renders the about page with flow and tech sections", () => {
    render(
      <MemoryRouter>
        <About />
      </MemoryRouter>
    );
    expect(screen.getByRole("heading", { name: /About QueryGoa/i })).toBeInTheDocument();
    expect(screen.getByText("VOICE → RETRIEVAL → RERANK → GENERATION → GUARDRAILS")).toBeInTheDocument();
    expect(screen.getByText("Voice")).toBeInTheDocument();
    expect(screen.getByText("Reranking")).toBeInTheDocument();
    expect(screen.getByText("Guardrails")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /Built for grounded conversations/i })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /Less noise\. More signal\./i })).toBeInTheDocument();
    expect(screen.getByText("Built for HH Goa 2026")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "About" })).toHaveAttribute("href", "/about");
  });
});