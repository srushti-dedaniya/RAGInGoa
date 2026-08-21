import { Link } from "react-router-dom";
import VoiceOrb from "../../components/VoiceOrb/VoiceOrb";
import QueryWorkspace from "../../components/QueryWorkspace/QueryWorkspace";
import Guardrails from "../../components/Guardrails/Guardrails";
import Benchmark from "../../components/Benchmark/Benchmark";

export default function Ask() {
  return (
    <main className="relative min-h-screen bg-cream">
      <div aria-hidden="true" className="fixed inset-0 z-0">
        <img
          src="/rag-background.jpeg"
          alt=""
          className="w-full h-full object-cover object-center"
          loading="eager"
          decoding="async"
        />
        <div className="absolute inset-0 bg-paper/10" />
      </div>

      <header className="sticky top-0 z-40 bg-paper/15 backdrop-blur-[2px] border-b border-paper/25 px-margin-mobile md:px-margin-desktop py-4 flex items-center justify-between gap-4">
        <Link
          to="/"
          className="brand-logo font-display-serif font-semibold text-sea text-xl tracking-tight leading-none uppercase drop-shadow-[0_1px_1px_rgba(250,244,228,0.6)]"
        >
          QueryGoa
        </Link>
        <Link
          to="/"
          className="font-dm-sans text-[12.5px] font-medium uppercase tracking-[0.08em] text-sea-deep hover:text-terracotta transition-colors inline-flex items-center gap-2 bg-paper/30 backdrop-blur-[2px] rounded-full px-3 py-1.5"
        >
          <span aria-hidden="true">←</span> Back to Home
        </Link>
      </header>

      <section className="relative z-10 px-margin-mobile md:px-margin-desktop min-h-[calc(100vh-64px)] flex flex-col items-center justify-center pt-8 pb-8">
        <VoiceOrb />
        <p className="font-dm-sans text-[17px] leading-[1.7] font-normal tracking-[0.01em] text-sea-deep mt-8 max-w-xl text-center bg-paper/60 backdrop-blur-[2px] rounded-full px-5 py-2">
          Tap the circle and ask in your voice — or type a question below.
        </p>
      </section>

      <div className="relative z-10">
        <QueryWorkspace />
      </div>

      <div className="relative z-10">
        <Guardrails />
      </div>

      <div className="relative z-10">
        <Benchmark />
      </div>
    </main>
  );
}