import { useRAG } from "../../context/RAGContext";
import { formatDuration } from "../../utils/formatTime";

export default function SystemStatus() {
  const { health, isOnline, demoMode } = useRAG();
  const routers = health?.routers || {};

  return (
    <section id="system" className="px-margin-mobile md:px-margin-desktop py-12">
      <div className="max-w-5xl mx-auto">
        <div
          className={`border-2 rounded-xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-6 ${
            isOnline ? "border-primary bg-primary-container/5" : "border-error bg-error-container/10"
          }`}
        >
          <div className="flex items-center gap-4">
            <div
              className={`w-4 h-4 rounded-full animate-pulse ${isOnline ? "bg-accent-yellow" : "bg-error"}`}
            />
            <div>
              <h2 className="font-headline-lg text-headline-lg-mobile uppercase text-primary">
                {isOnline ? "System Online" : "System Degraded"}
              </h2>
              <p className="font-meta-mono text-meta-mono uppercase text-secondary">
                v{health?.version || "1.0.0"} · up {formatDuration(health?.uptime_seconds)}
              </p>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            <RouterChip label="STT" value={routers.stt} />
            <RouterChip label="LLM" value={routers.llm} />
            <RouterChip label="VectorDB" value={routers.vector_db} />
            <span className="chip bg-surface-variant text-on-surface">
              index: <strong>{health?.index_size ?? 0}</strong>
            </span>
          </div>
        </div>

        {demoMode && (
          <p className="mt-4 text-center font-meta-mono text-meta-mono uppercase text-tertiary">
            demo mode — canned responses (backend offline)
          </p>
        )}
      </div>
    </section>
  );
}

function RouterChip({ label, value }) {
  return (
    <span className="chip bg-surface text-on-surface">
      {label}: <span className="text-primary">{value || "—"}</span>
    </span>
  );
}
