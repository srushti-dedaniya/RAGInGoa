import { Link } from "react-router-dom";

export default function FinalCTA() {
  return (
    <section id="cta" className="px-margin-mobile md:px-margin-desktop py-24">
      <div className="relative max-w-3xl mx-auto text-center border-2 border-sea bg-paper/95 rounded-xl p-10 md:p-14 shadow-[6px_6px_0_0_rgba(14,81,69,0.2)]">
        <span className="chip bg-sand/60 text-sea-deep border-sea/30">GET STARTED</span>
        <h2 className="font-display-serif italic font-semibold text-sea mt-5 text-4xl md:text-5xl leading-tight">
          Ready to ask <span className="text-terracotta">your question?</span>
        </h2>
        <p className="font-refined-sans text-[16.5px] leading-[1.7] text-sea-deep/80 mt-4 max-w-xl mx-auto">
          Head to the RAG workspace — ask with your voice or type it out, and get a grounded
          answer with cited sources.
        </p>
        <Link
          to="/ask"
          className="mt-8 inline-flex items-center gap-3 bg-terracotta text-paper font-refined-sans text-[13px] font-semibold uppercase tracking-[0.14em] px-8 py-4 border-2 border-sea-deep shadow-[3px_3px_0_0_#0A3E35] hover:translate-x-[1px] hover:translate-y-[1px] hover:shadow-[1px_1px_0_0_#0A3E35] transition-all"
        >
          Ask Now <span aria-hidden="true">→</span>
        </Link>
      </div>
    </section>
  );
}