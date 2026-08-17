import { ragService } from "./ragService";

const MIME_TYPES = [
  "audio/webm",
  "audio/webm;codecs=opus",
  "audio/mp4",
  "audio/ogg",
];

function pickMime() {
  if (typeof MediaRecorder === "undefined") return null;
  return MIME_TYPES.find((t) => MediaRecorder.isTypeSupported(t)) || "";
}

export function isVoiceSupported() {
  return (
    typeof window !== "undefined" &&
    Boolean(navigator.mediaDevices?.getUserMedia) &&
    typeof MediaRecorder !== "undefined"
  );
}

export async function recordVoice({ onChunk = null, onStop = null } = {}) {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  const mimeType = pickMime();
  const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
  const chunks = [];

  recorder.addEventListener("dataavailable", (event) => {
    if (event.data.size > 0) {
      chunks.push(event.data);
      if (onChunk) onChunk(chunks);
    }
  });

  const stopPromise = new Promise((resolve) => {
    recorder.addEventListener("stop", async () => {
      stream.getTracks().forEach((track) => track.stop());
      const blob = new Blob(chunks, { type: recorder.mimeType || mimeType || "audio/webm" });
      if (onStop) onStop(blob);
      resolve(blob);
    });
  });

  recorder.start();
  return { recorder, done: stopPromise };
}

export async function transcribeBlob(blob) {
  return ragService.transcribeAudio(blob);
}
