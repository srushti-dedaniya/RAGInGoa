import Pipeline from "./Pipeline";
import { useScrollAnimation } from "../../hooks/useScrollAnimation";

const STAGE_DETAILS = [
  {
    id: "stt",
    title: "Transcribe",
    body: "Your voice becomes text. Dev router returns a canned transcript; the whisper router runs OpenAI Whisper for real audio.",
  },
  {
    id: "retrieval",
    title: "Retrieve",
    body: "The query is embedded and searched against a vector index of Goa context. Only the most relevant chunks come back.",
  },
  {
    id: "rerank",
    title: "Rerank",
    body: "A second pass re-orders hits by lexical + cosine blend so the strongest evidence leads the context window.",
  },
  {
    id: "generation",
    title: "Generate",
    body: "The LLM answers strictly from the retrieved passages, citing sources inline. Dev mode produces a grounded extractive answer.",
  },
  {
    id: "guardrails",
    title: "Guard",
    body: "Safety, relevance, grounding and refusal checks run last. Anything that can't be grounded is refused or flagged.",
  },
];

export default function PipelineSection() {
  const { ref, inView } = useScrollAnimation();

  return (
    <section id="pipeline" className="px-margin-mobile md:px-margin-desktop py-16 bg-surface-container/40">
      <div className="max-w-5xl mx-auto" ref={ref}>
        <div className="text-center mb-10">
          <span className="chip bg-accent-yellow text-on-surface">PIPELINE</span>
          <h2 className="font-headline-lg text-headline-lg-mobile uppercase text-primary mt-4">
            How it works
          </h2>
          <p className="font-meta-mono text-meta-mono uppercase text-secondary mt-2">
            STT → RETRIEVAL → RERANK → GENERATION → GUARDRAILS
          </p>
        </div>

        <Pipeline compact />

        <div className={`mt-10 grid grid-cols-1 md:grid-cols-5 gap-4 ${inView ? "staggered-item" : "staggered-item"}`}>
          {STAGE_DETAILS.map((stage) => (
            <article key={stage.id} className="border border-outline-variant bg-surface rounded-lg p-4">
              <span className="font-meta-mono text-meta-mono uppercase text-tertiary">0{STAGE_DETAILS.indexOf(stage) + 1}</span>
              <h3 className="font-body-bold text-body-bold text-primary uppercase mt-1">{stage.title}</h3>
              <p className="font-body-md text-body-md text-on-surface-variant text-sm mt-2">{stage.body}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
