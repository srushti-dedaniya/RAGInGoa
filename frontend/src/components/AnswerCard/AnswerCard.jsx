import { useEffect, useRef, useState } from "react";
import { formatLatency } from "../../utils/formatLatency";
import { formatTime } from "../../utils/formatTime";
import { ragService } from "../../services/ragService";
import Icon from "../Icon/Icon";

export function cleanAnswer(text = "") {
  return text
    .replace(/\s*\[Source:\s*[^\]]+\]/gi, "")
    .replace(/\bmsmarco-xi-[\w-]+\b/gi, "")
    .replace(/\s+([.,!?।])/g, "$1")
    .trim();
}

export default function AnswerCard({ result, isProcessing = false, languageCode = "en-IN" }) {
  const [audioState, setAudioState] = useState("idle");
  const [audioError, setAudioError] = useState("");
  const audioRef = useRef(null);
  const audioUrlRef = useRef("");

  const releaseAudio = () => {
    audioRef.current?.pause();
    audioRef.current = null;
    if (audioUrlRef.current) URL.revokeObjectURL(audioUrlRef.current);
    audioUrlRef.current = "";
  };

  useEffect(() => {
    releaseAudio();
    setAudioState("idle");
    setAudioError("");
    return releaseAudio;
  }, [result?.answer, languageCode]);

  if (!result) return null;

  const breakdown = result.latency_breakdown || {};
  const visibleAnswer = cleanAnswer(result.answer);
  const isConversation = result.intermediate?.input_class === "conversational";

  const listen = async () => {
    setAudioError("");
    if (audioState === "playing") {
      audioRef.current?.pause();
      setAudioState("paused");
      return;
    }
    if (audioRef.current) {
      if (audioRef.current.ended) audioRef.current.currentTime = 0;
      await audioRef.current.play();
      setAudioState("playing");
      return;
    }
    setAudioState("loading");
    try {
      const blob = await ragService.synthesize(visibleAnswer, { languageCode });
      releaseAudio();
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      audioUrlRef.current = url;
      audioRef.current = audio;
      audio.onended = () => setAudioState("ready");
      audio.onerror = () => {
        setAudioError("The generated audio could not be played.");
        setAudioState("error");
      };
      await audio.play();
      setAudioState("playing");
    } catch (error) {
      releaseAudio();
      setAudioError(error.message || "Unable to read this answer aloud.");
      setAudioState("error");
    }
  };

  const stop = () => {
    if (audioRef.current) audioRef.current.currentTime = 0;
    audioRef.current?.pause();
    setAudioState("ready");
  };

  return (
    <article className="relative border-2 border-primary bg-surface-container-low rounded-xl p-6 offset-shadow" id="answer">
      <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
        <div className="flex items-center gap-3">
          <Icon name={result.grounded ? "verified" : "info"} size={22} className="text-primary" />
          <h3 className="font-display-serif italic font-semibold text-primary">
            {result.grounded || isConversation ? "Answer" : "Insufficient Context"}
          </h3>
        </div>
        <div className="flex items-center gap-2 font-dm-sans text-[12px] font-medium uppercase tracking-[0.08em]">
          <span className="chip bg-surface-variant">{formatTime()}</span>
        </div>
      </div>

      {isProcessing ? (
        <div className="flex items-center gap-3 text-on-surface-variant">
          <Icon name="progress_activity" size={20} className="animate-spin text-primary" />
          <span className="font-dm-sans text-[12px] font-medium uppercase tracking-[0.08em]">generating grounded answer…</span>
        </div>
      ) : (
        <>
          <p className="font-dm-sans text-[16px] leading-[1.7] text-on-surface whitespace-pre-line" aria-live="polite">
            {visibleAnswer}
          </p>

          <div className="mt-4 flex flex-wrap items-center gap-2">
            <button
              type="button"
              onClick={listen}
              disabled={audioState === "loading" || !visibleAnswer}
              aria-label={audioState === "playing" ? "Pause answer" : "Listen to answer"}
              className="chip border border-primary bg-surface text-primary hover:bg-primary hover:text-on-primary transition-colors disabled:opacity-50"
            >
              <span aria-hidden="true">{audioState === "playing" ? "⏸" : "🔊"}</span>
              {audioState === "loading" ? "Preparing…" : audioState === "playing" ? "Pause" : audioState === "paused" ? "Resume" : audioState === "ready" ? "Replay" : "Listen"}
            </button>
            {(audioState === "playing" || audioState === "paused") && (
              <button type="button" onClick={stop} className="chip border border-outline-variant bg-surface text-on-surface-variant hover:border-primary">
                Stop
              </button>
            )}
            {audioError && <span role="alert" className="font-meta-mono text-meta-mono text-error">{audioError}</span>}
          </div>

          <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            <LatencyTile label="Retrieval" ms={breakdown.retrieval} icon="database" />
            <LatencyTile label="Generation" ms={breakdown.generation} icon="auto_awesome" />
            <LatencyTile label="Guardrails" ms={breakdown.guardrails} icon="verified_user" />
            <LatencyTile label="Total" ms={breakdown.total} icon="timer" highlight />
          </div>

          {result.warnings?.length > 0 && (
            <div className="mt-4 border border-dotted border-error rounded-lg px-4 py-3 font-dm-sans text-[13px] text-error">
              {result.warnings.map((w) => (
                <p key={w}>⚠ {w}</p>
              ))}
            </div>
          )}
        </>
      )}
    </article>
  );
}

function LatencyTile({ label, ms, icon, highlight = false }) {
  return (
    <div
      className={`rounded-lg border px-3 py-2 ${
        highlight ? "bg-primary text-on-primary border-primary" : "bg-surface border-outline-variant"
      }`}
    >
      <div className="flex items-center gap-1.5 font-dm-sans text-[12px] font-medium uppercase tracking-[0.08em] opacity-80">
        <Icon name={icon} size={14} />
        {label}
      </div>
      <div className="font-dm-sans text-[16px] font-semibold">{formatLatency(ms)}</div>
    </div>
  );
}
