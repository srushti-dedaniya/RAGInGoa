import { apiGet, apiPost, apiPostBlob } from "./api";
import { DEMO_RESULT, DEMO_BENCHMARK, DEMO_HEALTH } from "../utils/constants";

const demoQuery = import.meta.env.VITE_DEMO_QUERY || "";

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function audioFilename(blob) {
  const type = (blob?.type || "audio/webm").split(";", 1)[0];
  const extensions = {
    "audio/webm": "webm", "video/webm": "webm", "audio/mp4": "m4a",
    "audio/ogg": "ogg", "audio/mpeg": "mp3", "audio/wav": "wav",
  };
  return `recording.${extensions[type] || "webm"}`;
}

export class RagService {
  constructor({ demo = false } = {}) {
    this.demo = demo;
  }

  async runQuery(query, { onStage = null, topK = null, languageCode = "en-IN" } = {}) {
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
      if (onStage) onStage("retrieval");
      const payload = { query, language_code: languageCode };
      if (topK) payload.top_k = topK;
      const data = await apiPost("/query", payload);
      if (onStage) onStage("guardrails");
      return data;
    } catch (error) { throw error; }
  }

  async getHealth() {
    if (this.demo) return DEMO_HEALTH;
    try {
      return await apiGet("/health", 4000);
    } catch {
      return { status: "OFFLINE", ready: false };
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

  async transcribeAudio(blob, { languageCode = "unknown" } = {}) {
    if (this.demo) {
      await sleep(400);
      return { transcript: demoQuery, confidence: 1.0, engine: "dev-stt" };
    }
    const form = new FormData();
    form.append("file", blob, audioFilename(blob));
    try {
      return await apiPost(`/transcribe?language_code=${encodeURIComponent(languageCode)}`, form, 30000);
    } catch (error) { throw error; }
  }

  async runVoice(blob, { topK = null, languageCode = "unknown" } = {}) {
    const form = new FormData();
    form.append("file", blob, audioFilename(blob));
    const params = new URLSearchParams({ language_code: languageCode });
    if (topK) params.set("top_k", String(topK));
    return apiPost(`/rag/voice?${params}`, form, 60000);
  }

  async synthesize(text, { languageCode = "en-IN" } = {}) {
    if (this.demo) throw new Error("Text-to-speech is unavailable in demo mode.");
    return apiPostBlob("/tts", { text, language_code: languageCode }, 45000);
  }

  get defaultQuery() {
    return demoQuery;
  }
}

export const ragService = new RagService({ demo: import.meta.env.VITE_USE_DEMO === "true" });
