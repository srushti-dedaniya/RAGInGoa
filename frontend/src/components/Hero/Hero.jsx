import { Link } from "react-router-dom";

export default function Hero() {
  return (
    <section id="top" className="relative min-h-[92vh] md:min-h-screen flex items-center overflow-hidden bg-cream">
      <img src="/goa-hero.jpeg" alt="Vintage Goa coastline illustration with a lighthouse, palm trees, ocean and sailing boats" className="absolute inset-0 w-full h-full object-cover object-[70%_40%] md:object-center" loading="eager" decoding="async" />
      <div className="relative z-10 w-full px-margin-mobile md:px-margin-desktop py-24">
        <div className="max-w-2xl">
          <h1 className="hero-heading font-display-serif italic font-semibold leading-[1.08] tracking-tight text-[clamp(2.9rem,7.2vw,5.75rem)] drop-shadow-[0_2px_2px_rgba(250,244,228,0.7)]">
            <span className="block text-sea">Ask Freely,</span>
            <span className="block text-terracotta">Get Clearly.</span>
          </h1>
          <p className="mt-6 font-refined-sans text-[17px] leading-[1.7] font-normal tracking-[0.01em] text-sea-deep max-w-md">Speak your question. We&apos;ll understand,<br />search, and bring you the right answer.</p>
          <Link to="/ask" className="mt-8 inline-flex items-center gap-3 bg-sea text-paper font-refined-sans text-[13px] font-semibold uppercase tracking-[0.14em] px-6 py-3 border-2 border-sea-deep shadow-[2px_2px_0_0_#0A3E35] hover:translate-x-[1px] hover:translate-y-[1px] hover:shadow-[1px_1px_0_0_#0A3E35] transition-all">Explore Now <span aria-hidden="true">→</span></Link>
        </div>
      </div>
    </section>
  );
}
