import { formatLatency } from "../../utils/formatLatency";
import { formatTime } from "../../utils/formatTime";
import Icon from "../Icon/Icon";

export default function AnswerCard({ result, isProcessing = false }) {
  if (!result) return null;

  const breakdown = result.latency_breakdown || {};
  const engine = result.engine || {};

  return (
    <article className="relative border-2 border-primary bg-surface-container-low rounded-xl p-6 offset-shadow" id="answer">
      <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
        <div className="flex items-center gap-3">
          <Icon name="verified" size={22} className="text-primary" />
          <h3 className="font-headline-lg text-headline-lg-mobile uppercase text-primary">Grounded Answer</h3>
        </div>
        <div className="flex items-center gap-2 font-meta-mono text-meta-mono uppercase">
          <span className="chip bg-surface-variant">{result.grounded ? "Grounded" : "Not grounded"}</span>
          <span className="chip bg-surface-variant">{formatTime()}</span>
        </div>
      </div>

      {isProcessing ? (
        <div className="flex items-center gap-3 text-on-surface-variant">
          <Icon name="progress_activity" size={20} className="animate-spin text-primary" />
          <span className="font-meta-mono text-meta-mono uppercase">generating grounded answer…</span>
        </div>
      ) : (
        <>
          <p className="font-body-md text-body-md text-on-surface whitespace-pre-line leading-relaxed" aria-live="polite">
            {result.answer}
          </p>

          <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            <LatencyTile label="Retrieval" ms={breakdown.retrieval} icon="database" />
            <LatencyTile label="Generation" ms={breakdown.generation} icon="auto_awesome" />
            <LatencyTile label="Guardrails" ms={breakdown.guardrails} icon="verified_user" />
            <LatencyTile label="Total" ms={breakdown.total} icon="timer" highlight />
          </div>

          <div className="mt-4 flex flex-wrap items-center gap-2">
            <span className="font-label-caps text-label-caps uppercase text-secondary">Engine</span>
            <EngineChip label="STT" value={engine.stt} />
            <EngineChip label="LLM" value={engine.llm} />
            <EngineChip label="VectorDB" value={engine.vector_db} />
            <EngineChip label="Embedding" value={engine.embedding} />
          </div>

          {result.warnings?.length > 0 && (
            <div className="mt-4 border border-dotted border-error rounded-lg px-4 py-3 font-meta-mono text-meta-mono text-error">
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
      <div className="flex items-center gap-1.5 font-meta-mono text-meta-mono uppercase opacity-80">
        <Icon name={icon} size={14} />
        {label}
      </div>
      <div className="font-body-bold text-body-bold">{formatLatency(ms)}</div>
    </div>
  );
}

function EngineChip({ label, value }) {
  return (
    <span className="chip bg-surface text-on-surface-variant">
      {label}: <span className="text-primary">{value || "—"}</span>
    </span>
  );
}
