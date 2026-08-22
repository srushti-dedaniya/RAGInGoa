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
        for (const stage of ["listening", "transcribing", "retrieving", "generating"]) {
          onStage(stage);
          await sleep(120);
        }
      }
      await sleep(150);
      return { ...DEMO_RESULT, query: query || DEMO_RESULT.query };
    }

    let generateTimer = null;
    try {
      const payload = { query, language_code: languageCode };
      if (topK) payload.top_k = topK;
      if (onStage) {
        onStage("retrieving");
        generateTimer = setTimeout(() => onStage("generating"), 900);
      }
      return await apiPost("/query", payload);
    } finally { if (generateTimer) clearTimeout(generateTimer); }
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
    return apiPost(`/transcribe?language_code=${encodeURIComponent(languageCode)}`, form, 30000);
  }

  async runVoice(blob, { topK = null, languageCode = "unknown", fallbackQuery = "", onStage = null } = {}) {
    const notify = (stage) => { if (onStage) onStage(stage); };

    if (this.demo) {
      for (const stage of ["listening", "transcribing", "retrieving", "generating"]) {
        notify(stage);
        await sleep(120);
      }
      return { ...DEMO_RESULT, query: fallbackQuery || DEMO_RESULT.query };
    }

    notify("transcribing");
    const form = new FormData();
    form.append("file", blob, audioFilename(blob));
    const params = new URLSearchParams({ language_code: languageCode });
    const transcriptData = await apiPost(`/transcribe?${params}`, form, 30000);
    let transcript = (transcriptData?.transcript || "").trim();
    if (!transcript && fallbackQuery.trim()) transcript = fallbackQuery.trim();
    if (!transcript) {
      const error = new Error("Couldn't understand the recording. Please try again.");
      error.code = "speech_not_understood";
      throw error;
    }
    const data = await this.runQuery(transcript, { topK, languageCode, onStage });
    return { ...data, voice_fallback: transcript === fallbackQuery.trim() || undefined };
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
