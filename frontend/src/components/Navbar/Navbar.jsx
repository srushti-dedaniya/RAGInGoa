import { useRAG } from "../../context/RAGContext";

const LINKS = [
  { href: "#how-it-works", label: "How it works" },
  { href: "#pipeline", label: "Pipeline" },
  { href: "#performance", label: "Performance" },
  { href: "#team", label: "Team" },
];

export default function Navbar() {
  const { isOnline } = useRAG();

  const tryVoice = () => {
    window.dispatchEvent(new CustomEvent("rag:voice"));
    document.getElementById("query")?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <nav
      aria-label="Primary"
      className="w-full top-0 sticky z-50 bg-background/90 backdrop-blur-sm border-b border-dotted border-primary flex justify-between items-center px-margin-mobile md:px-margin-desktop py-4"
    >
      <a href="#top" className="font-headline-lg text-primary tracking-tight uppercase text-2xl">
        RAGInGoa
      </a>
      <div className="hidden md:flex gap-6 items-center">
        {LINKS.map((link) => (
          <a key={link.href} href={link.href} className="section-anchor py-2">
            {link.label}
          </a>
        ))}
        <div className="font-meta-mono text-meta-mono uppercase text-primary border border-primary px-3 py-1 rounded-full flex items-center gap-2">
          <span aria-hidden="true" className={`w-2 h-2 rounded-full animate-pulse ${isOnline ? "bg-accent-yellow" : "bg-error"}`} />
          {isOnline ? "SYSTEM ONLINE" : "SYSTEM DEGRADED"}
        </div>
        <button
          type="button"
          onClick={tryVoice}
          className="bg-tertiary text-on-tertiary font-label-caps text-label-caps uppercase px-6 py-3 border-2 border-primary offset-shadow hover:bg-tertiary-container transition-all"
        >
          TRY VOICE
        </button>
      </div>
      <button
        type="button"
        onClick={tryVoice}
        className="md:hidden bg-tertiary text-on-tertiary font-label-caps text-label-caps uppercase px-4 py-2 border-2 border-primary offset-shadow text-xs"
      >
        VOICE
      </button>
    </nav>
  );
}
