import { Link } from "react-router-dom";
import Navbar from "../../components/Navbar/Navbar";

const DESTINATIONS = [
  {
    name: "Palolem",
    tagline: "South Goa · Calm waters",
    description: "Quiet shores, turquoise waters, and laid-back beach vibes.",
    position: "center 20%",
  },
  {
    name: "Anjuna",
    tagline: "North Goa · Bohemian",
    description: "Bohemian energy, coastal sunsets, markets, and nightlife.",
    position: "center 35%",
  },
  {
    name: "Baga",
    tagline: "North Goa · Lively",
    description: "One of Goa's liveliest beaches, packed with food, water sports, and nightlife.",
    position: "center 50%",
  },
  {
    name: "Panaji",
    tagline: "Capital · Heritage",
    description: "Goa's colorful capital, filled with heritage streets, culture, and riverside charm.",
    position: "center 65%",
  },
  {
    name: "Old Goa",
    tagline: "Historic · Colonial",
    description: "Historic churches, Portuguese heritage, and centuries of Goa's story.",
    position: "center 80%",
  },
  {
    name: "Morjim",
    tagline: "North Goa · Tranquil",
    description: "A peaceful coastal escape known for its relaxed atmosphere and scenic beach.",
    position: "center 95%",
  },
];

export default function Destinations() {
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

      <Navbar active="destinations" />

      <section className="relative z-10 px-margin-mobile md:px-margin-desktop pt-32 pb-10">
        <Link
          to="/"
          className="font-refined-sans text-[12.5px] font-medium uppercase tracking-[0.08em] text-sea-deep hover:text-terracotta transition-colors inline-flex items-center gap-2"
        >
          <span aria-hidden="true">←</span> Home
        </Link>
        <div className="mt-10 max-w-3xl">
          <span className="chip bg-sand/60 text-sea-deep border-sea/30">GOA, INDIA</span>
          <h1 className="hero-heading font-display-serif font-semibold text-sea mt-4 text-[clamp(2.75rem,6vw,4.75rem)]">
            Explore Goa
          </h1>
          <p className="mt-5 font-refined-sans text-[17px] leading-[1.7] text-sea-deep max-w-xl">
            From sun-kissed beaches to hidden corners, discover Goa through QueryGoa.
          </p>
        </div>
      </section>

      <section className="relative z-10 px-margin-mobile md:px-margin-desktop pb-24">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
          {DESTINATIONS.map((destination) => (
            <article
              key={destination.name}
              className="group overflow-hidden rounded-xl border border-sea/20 bg-paper shadow-[4px_4px_0_0_rgba(14,81,69,0.25)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0_0_rgba(14,81,69,0.35)] transition-all"
            >
              <div
                aria-hidden="true"
                className="h-40 bg-cover bg-center"
                style={{
                  backgroundImage: "url('/rag-background.jpeg')",
                  backgroundSize: "cover",
                  backgroundPosition: destination.position,
                  backgroundRepeat: "no-repeat",
                }}
              />
              <div className="p-6">
                <p className="font-meta-mono text-meta-mono uppercase text-terracotta">{destination.tagline}</p>
                <h2 className="font-display-serif font-semibold text-sea text-2xl mt-1">{destination.name}</h2>
                <p className="font-refined-sans text-[14.5px] leading-[1.65] text-on-surface-variant mt-3">
                  {destination.description}
                </p>
              </div>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}