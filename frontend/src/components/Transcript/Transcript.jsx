export default function Transcript({ isRecording = false, isSupported = true, level = 0, text = "", isTranscribing = false }) {
  const placeholder = !isSupported
    ? "Mic not available — type your question below."
    : isRecording
      ? "Listening…"
      : "What do you want to know about Goa?";

  const shownText = isTranscribing ? "" : text || placeholder;
  const meterFill = Math.min(1, Math.max(0.12, level * 3));

  return (
    <div className="glassmorphism rounded-xl px-6 py-4 border-2 border-dotted border-outline" role="status" aria-live="polite">
      <div className="flex items-center justify-between mb-2">
        <span className="font-dm-sans text-[12px] font-medium uppercase tracking-[0.08em] text-primary">Transcript</span>
        {isRecording && (
          <span className="flex items-center gap-2" aria-hidden="true">
            <span className="flex items-end gap-[3px] h-4">
              {[0.55, 0.8, 1, 0.8, 0.55].map((factor, i) => (
                <span
                  key={i}
                  className="w-[3px] h-full rounded-full bg-error transition-transform duration-100"
                  style={{ transform: `scaleY(${Math.max(0.15, meterFill * factor)})`, transformOrigin: "bottom" }}
                />
              ))}
            </span>
            <span className="font-dm-sans text-[12px] font-medium uppercase tracking-[0.08em] text-error animate-pulse">LIVE</span>
          </span>
        )}
        {isTranscribing && (
          <span className="font-dm-sans text-[12px] font-medium uppercase tracking-[0.08em] text-secondary animate-pulse">TRANSCRIBING…</span>
        )}
      </div>

      {isTranscribing ? (
        <div className="space-y-2 py-0.5" aria-label="Transcribing your speech">
          <span className="block h-3 w-3/4 rounded bg-outline-variant animate-pulse" />
          <span className="block h-3 w-1/2 rounded bg-outline-variant animate-pulse" />
        </div>
      ) : (
        <p className={`font-dm-sans text-[15.5px] leading-[1.6] ${text ? "text-on-surface" : "text-on-surface-variant"}`}>
          {shownText}
        </p>
      )}
    </div>
  );
}
