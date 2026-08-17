export default function Transcript({ isRecording = false, isSupported = true, level = 0, text = "" }) {
  const placeholder = !isSupported
    ? "Mic not available — type your question below."
    : isRecording
      ? "Listening…"
      : "What do you want to know about Goa?";

  return (
    <div className="glassmorphism rounded-xl px-6 py-4 border-2 border-dotted border-outline" role="status" aria-live="polite">
      <div className="flex items-center justify-between mb-2">
        <span className="font-label-caps text-label-caps uppercase text-primary">Transcript</span>
        <span
          className={`font-meta-mono text-meta-mono uppercase ${
            isRecording ? "text-error animate-pulse" : "text-secondary"
          }`}
        >
          {isRecording ? `LIVE · ${Math.round(level * 100)}` : "IDLE"}
        </span>
      </div>
      <p className={`font-body-md text-body-md ${text ? "text-on-surface" : "text-on-surface-variant"}`}>
        {text || placeholder}
      </p>
    </div>
  );
}
