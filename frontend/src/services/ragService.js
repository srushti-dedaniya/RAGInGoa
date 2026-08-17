import { apiGet, apiPost } from "./api";
import { DEMO_RESULT, DEMO_BENCHMARK, DEMO_HEALTH } from "../utils/constants";

const demoQuery = import.meta.env.VITE_DEMO_QUERY || "What is the best time to visit Palolem in Goa?";

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

export class RagService {
  constructor({ demo = false } = {}) {
    this.demo = demo;
  }

  async runQuery(query, { onStage = null, topK = null } = {}) {
    if (this.demo) {
      if (onStage) {
        for (const stage of ["stt", "retrieval", "rerank", "generation", "guardrails"]) {
          onStage(stage);
          await sleep(120);
        }
      }
      await sleep(150);
      return { ...DEMO_RESULT, query: query || DEMO_RESULT.query };
    }

    try {
      if (onStage) {
        onStage("stt");
        await sleep(60);
        onStage("retrieval");
        await sleep(60);
        onStage("rerank");
        await sleep(60);
        onStage("generation");
        await sleep(60);
      }
      const payload = { query };
      if (topK) payload.top_k = topK;
      const data = await apiPost("/query", payload);
      if (onStage) onStage("guardrails");
      return data;
    } catch (error) {
      this.demo = true;
      if (onStage) {
        for (const stage of ["stt", "retrieval", "rerank", "generation", "guardrails"]) {
          onStage(stage);
          await sleep(90);
        }
      }
      return { ...DEMO_RESULT, query: query || DEMO_RESULT.query, warnings: [error.message] };
    }
  }

  async getHealth() {
    if (this.demo) return DEMO_HEALTH;
    try {
      return await apiGet("/health", 4000);
    } catch {
      this.demo = true;
      return DEMO_HEALTH;
    }
  }

  async getBenchmark() {
    if (this.demo) return { report: DEMO_BENCHMARK };
    try {
      return await apiGet("/benchmark", 4000);
    } catch {
      return { report: DEMO_BENCHMARK };
    }
  }

  async runBenchmark() {
    if (this.demo) return { report: DEMO_BENCHMARK };
    try {
      return await apiPost("/benchmark", {}, 30000);
    } catch {
      return { report: DEMO_BENCHMARK };
    }
  }

  async transcribeAudio(blob) {
    if (this.demo) {
      await sleep(400);
      return { transcript: demoQuery, confidence: 1.0, engine: "dev-stt" };
    }
    const form = new FormData();
    form.append("file", blob, "recording.webm");
    try {
      return await apiPost("/transcribe", form, 30000);
    } catch {
      return { transcript: demoQuery, confidence: 1.0, engine: "dev-stt" };
    }
  }

  get defaultQuery() {
    return demoQuery;
  }
}

export const ragService = new RagService({ demo: import.meta.env.VITE_USE_DEMO === "true" });
