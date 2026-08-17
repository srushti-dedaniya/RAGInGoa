import { formatConfidence } from "../../utils/formatLatency";

export default function SourceCard({ source, index = 0 }) {
  const meta = source.metadata || {};
  const title = meta.title || `Source ${index + 1}`;
  const topic = meta.topic || "general";

  return (
    <article className="relative border border-outline-variant bg-surface-container-low rounded-lg p-4 hover:border-primary transition-colors flex flex-col gap-2">
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <span className="shrink-0 w-6 h-6 rounded-full bg-primary-container text-surface text-xs flex items-center justify-center font-meta-mono">
            {index + 1}
          </span>
          <h4 className="font-body-bold text-body-bold text-primary truncate">{title}</h4>
        </div>
        <span className="shrink-0 font-meta-mono text-meta-mono uppercase bg-accent-yellow text-on-surface px-2 py-0.5 rounded-full border border-primary">
          {topic}
        </span>
      </div>

      <p className="font-body-md text-body-md text-on-surface-variant text-sm line-clamp-3">{source.text}</p>

      <div className="mt-auto flex items-center justify-between pt-2 border-t border-dotted border-outline-variant">
        <span className="font-meta-mono text-meta-mono uppercase text-secondary">
          {formatConfidence(source.score)} · {source.score_type}
        </span>
        <button
          type="button"
          onClick={() => navigator.clipboard?.writeText(source.chunk_id)}
          className="font-label-caps text-label-caps uppercase text-tertiary hover:underline"
          title={`Copy chunk id: ${source.chunk_id}`}
        >
          cite
        </button>
      </div>
    </article>
  );
}
