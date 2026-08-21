import Icon from "../../components/Icon/Icon";

const FEATURES = [
  {
    icon: "mic",
    title: "Ask in your voice",
    body: "Speak naturally — speech-to-text turns your question into a query in a blink.",
  },
  {
    icon: "database",
    title: "Goa context",
    body: "Retrieval runs over a curated Goa corpus, not a generic web search.",
  },
  {
    icon: "verified_user",
    title: "Grounded answers",
    body: "Every answer cites its sources and stays firmly on the evidence.",
  },
  {
    icon: "shield",
    title: "Guardrailed by default",
    body: "Safety, relevance, grounding and refusal checks run on every answer.",
  },
];

export default function WhyQueryGoa() {
  return (
    <section id="why" className="px-margin-mobile md:px-margin-desktop py-20">
      <div className="relative max-w-5xl mx-auto">
        <div className="text-center mb-12">
          <span className="chip bg-sand/60 text-sea-deep border-sea/30">WHY QUERYGOA</span>
          <h2 className="font-display-serif italic font-semibold text-sea mt-4 text-4xl md:text-5xl leading-tight">
            Ask Goa. <span className="text-terracotta">Get answers.</span>
          </h2>
          <p className="font-meta-mono text-meta-mono uppercase text-sea-deep/70 mt-3">
            VOICE IN · GROUNDED OUT · SOURCES CITED
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {FEATURES.map((feature) => (
            <article
              key={feature.title}
              className="border border-sea/20 bg-paper rounded-xl p-6 shadow-[3px_3px_0_0_rgba(14,81,69,0.25)] hover:translate-x-[1px] hover:translate-y-[1px] transition-all"
            >
              <div className="w-11 h-11 rounded-full bg-sea text-paper flex items-center justify-center mb-4">
                <Icon name={feature.icon} size={22} />
              </div>
              <h3 className="font-refined-sans text-[14px] font-semibold uppercase tracking-[0.1em] text-sea">{feature.title}</h3>
              <p className="font-refined-sans text-[14.5px] leading-[1.65] text-on-surface-variant mt-2">{feature.body}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}