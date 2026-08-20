export default function Transcript({ isRecording = false, isSupported = true, level = 0, text = "" }) {
  const placeholder = !isSupported
    ? "Mic not available — type your question below."
    : isRecording
      ? "Listening…"
      : "What do you want to know about Goa?";

  return (
    <div className="glassmorphism rounded-xl px-6 py-4 border-2 border-dotted border-outline" role="status" aria-live="polite">
      <div className="flex items-center justify-between mb-2">
        <span className="font-dm-sans text-[12px] font-medium uppercase tracking-[0.08em] text-primary">Transcript</span>
        <span
          className={`font-dm-sans text-[12px] font-medium uppercase tracking-[0.08em] ${
            isRecording ? "text-error animate-pulse" : "text-secondary"
          }`}
        >
          {isRecording ? `LIVE · ${Math.round(level * 100)}` : "IDLE"}
        </span>
      </div>
      <p className={`font-dm-sans text-[15.5px] leading-[1.6] ${text ? "text-on-surface" : "text-on-surface-variant"}`}>
        {text || placeholder}
      </p>
    </div>
  );
}
