import { Link } from "react-router-dom";
import Navbar from "../../components/Navbar/Navbar";
import Icon from "../../components/Icon/Icon";

const FLOW_STEPS = [
  {
    icon: "mic",
    title: "Voice",
    body: "Speak your question naturally.",
  },
  {
    icon: "database",
    title: "Retrieval",
    body: "Relevant Goa context is retrieved from the knowledge base.",
  },
  {
    icon: "swap_vert",
    title: "Reranking",
    body: "The most useful context is prioritized.",
  },
  {
    icon: "auto_awesome",
    title: "Generation",
    body: "The system generates an answer grounded in the retrieved information.",
  },
  {
    icon: "verified_user",
    title: "Guardrails",
    body: "Safety, relevance, grounding, and refusal checks verify the response.",
  },
];

const TECHNOLOGIES = [
  "React + Vite frontend",
  "FastAPI backend",
  "RAG pipeline (chunking, embeddings, vector search)",
  "Reranking & guardrails",
  "Web Speech API voice input",
];

export default function About() {
  return (
    <main className="relative min-h-screen overflow-x-hidden">
      <div
        aria-hidden="true"
        className="absolute inset-0"
        style={{
          backgroundImage: "url('/rag-background.jpeg')",
          backgroundSize: "cover",
          backgroundPosition: "center top",
          backgroundRepeat: "no-repeat",
          backgroundAttachment: "scroll",
        }}
      />
      <div aria-hidden="true" className="absolute inset-0 bg-cream/75" />

      <Navbar active="about" />

      <section className="relative z-10 px-margin-mobile md:px-margin-desktop pt-32 pb-10">
        <Link
          to="/"
          className="font-refined-sans text-[12.5px] font-medium uppercase tracking-[0.08em] text-sea-deep hover:text-terracotta transition-colors inline-flex items-center gap-2"
        >
          <span aria-hidden="true">←</span> Home
        </Link>
        <div className="mt-10 max-w-3xl">
          <span className="chip bg-sand/60 text-sea-deep border-sea/30">ABOUT QUERYGOA</span>
          <h1 className="hero-heading font-display-serif font-semibold text-sea mt-4 text-[clamp(2.75rem,6vw,4.75rem)]">
            About <span className="text-terracotta">QueryGoa</span>
          </h1>
          <p className="mt-5 font-refined-sans text-[17px] leading-[1.7] text-sea-deep max-w-xl">
            Ask naturally. Discover Goa. Get grounded answers.
          </p>
        </div>
      </section>

      <section className="relative z-10 px-margin-mobile md:px-margin-desktop pb-16">
        <div className="max-w-3xl mx-auto">
          <p className="font-refined-sans text-[16.5px] leading-[1.75] text-sea-deep/90">
            QueryGoa is a voice-first Retrieval-Augmented Generation experience designed to help
            people explore Goa through grounded answers. Instead of relying on generic responses,
            QueryGoa retrieves relevant Goa-specific context before generating an answer.
          </p>
        </div>
      </section>

      <section className="relative z-10 px-margin-mobile md:px-margin-desktop pb-16">
        <div className="max-w-3xl mx-auto">
          <p className="font-meta-mono text-meta-mono uppercase text-terracotta mb-8">
            VOICE → RETRIEVAL → RERANK → GENERATION → GUARDRAILS
          </p>
          <div className="flex flex-col gap-4">
            {FLOW_STEPS.map((step) => (
              <article
                key={step.title}
                className="border border-sea/20 bg-paper rounded-xl p-6 shadow-[3px_3px_0_0_rgba(14,81,69,0.2)]"
              >
                <div className="flex items-start gap-4">
                  <div className="w-11 h-11 shrink-0 rounded-full bg-sea text-paper flex items-center justify-center">
                    <Icon name={step.icon} size={22} />
                  </div>
                  <div>
                    <h2 className="font-refined-sans text-[14px] font-semibold uppercase tracking-[0.1em] text-sea">
                      {step.title}
                    </h2>
                    <p className="font-refined-sans text-[14.5px] leading-[1.65] text-on-surface-variant mt-1.5">
                      {step.body}
                    </p>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="relative z-10 px-margin-mobile md:px-margin-desktop pb-16">
        <div className="max-w-3xl mx-auto">
          <span className="chip bg-sand/60 text-sea-deep border-sea/30">TECHNOLOGY</span>
          <h2 className="font-display-serif italic font-semibold text-sea mt-4 text-3xl md:text-4xl leading-tight">
            Built for <span className="text-terracotta">grounded conversations</span>
          </h2>
          <ul className="mt-6 grid grid-cols-1 sm:grid-cols-2 gap-3">
            {TECHNOLOGIES.map((item) => (
              <li
                key={item}
                className="border border-sea/20 bg-paper rounded-xl px-4 py-3 font-refined-sans text-[14px] font-medium text-sea-deep flex items-center gap-2"
              >
                <Icon name="check" size={16} className="text-terracotta" />
                {item}
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="relative z-10 px-margin-mobile md:px-margin-desktop pb-24 text-center">
        <h2 className="font-display-serif italic font-semibold text-sea text-3xl md:text-4xl">
          Less noise. <span className="text-terracotta">More signal.</span>
        </h2>
        <p className="font-meta-mono text-meta-mono uppercase text-sea-deep/70 mt-3">
          Built for HH Goa 2026
        </p>
      </section>
    </main>
  );
}