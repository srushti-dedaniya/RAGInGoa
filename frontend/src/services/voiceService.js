import { ragService } from "./ragService";

const MIME_TYPES = [
  "audio/webm;codecs=opus",
  "audio/webm",
  "audio/mp4",
  "audio/ogg;codecs=opus",
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

function startLevelMeter(stream, onLevel) {
  if (typeof onLevel !== "function") return () => {};
  const AudioContextClass = window.AudioContext || window.webkitAudioContext;
  if (!AudioContextClass) return () => {};

  let rafId = null;
  let closed = false;
  try {
    const context = new AudioContextClass();
    const source = context.createMediaStreamSource(stream);
    const analyser = context.createAnalyser();
    analyser.fftSize = 512;
    source.connect(analyser);
    const data = new Uint8Array(analyser.fftSize);
    Promise.resolve(context.resume?.()).catch(() => {});

    const tick = () => {
      if (closed) return;
      analyser.getByteTimeDomainData(data);
      let sumSquares = 0;
      for (let i = 0; i < data.length; i += 1) {
        const centered = (data[i] - 128) / 128;
        sumSquares += centered * centered;
      }
      const rms = Math.sqrt(sumSquares / data.length);
      const level = Math.min(1, rms * 3.2);
      onLevel(level);
      rafId = requestAnimationFrame(tick);
    };
    rafId = requestAnimationFrame(tick);

    return () => {
      closed = true;
      if (rafId !== null) cancelAnimationFrame(rafId);
      try {
        source.disconnect();
        Promise.resolve(context.close?.()).catch(() => {});
      } catch {
        return;
      }
    };
  } catch {
    return () => {};
  }
}

export async function recordVoice({ onChunk = null, onStop = null, onLevel = null } = {}) {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  const mimeType = pickMime();
  const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
  const chunks = [];
  const stopMeter = startLevelMeter(stream, onLevel);

  recorder.addEventListener("dataavailable", (event) => {
    if (event.data.size > 0) {
      chunks.push(event.data);
      if (onChunk) onChunk(chunks);
    }
  });

  const stopPromise = new Promise((resolve) => {
    recorder.addEventListener("stop", async () => {
      stopMeter();
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
