import { Link } from "react-router-dom";

const LINKS = [
  { to: "/", label: "Explore", key: "explore" },
  { to: "/ask", label: "Ask", key: "ask" },
  { to: "/destinations", label: "Destinations", key: "destinations" },
  { to: "/about", label: "About", key: "about" },
];

const ICON_SVG = {
  search: <><circle cx="11" cy="11" r="7" /><path d="m21 21-4.3-4.3" /></>,
  user: <><circle cx="12" cy="8" r="4" /><path d="M4 21v-1a8 8 0 0 1 16 0v1" /></>,
  menu: <><line x1="4" x2="20" y1="6.5" y2="6.5" /><line x1="4" x2="20" y1="12" y2="12" /><line x1="4" x2="20" y1="17.5" y2="17.5" /></>,
};
const ICON_BUTTON_CLASSES = "w-10 h-10 rounded-full border border-sea/50 text-sea flex items-center justify-center hover:bg-sea hover:text-paper transition-colors backdrop-blur-[2px]";
const LINK_CLASSES = "font-refined-sans text-[12.5px] font-medium uppercase tracking-[0.08em] text-sea-deep hover:text-terracotta transition-colors";

function IconButton({ name, label, onClick }) {
  return <button type="button" aria-label={label} onClick={onClick} className={ICON_BUTTON_CLASSES}><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" focusable="false">{ICON_SVG[name]}</svg></button>;
}

export default function Navbar({ active }) {
  return (
    <nav aria-label="Primary" className="fixed top-0 left-0 right-0 z-50 w-full bg-paper/40 backdrop-blur-[3px] border-b border-paper/20 px-margin-mobile md:px-margin-desktop py-3 flex items-center justify-between gap-4">
      <Link to="/" className="brand-logo font-display-serif font-semibold text-sea text-xl md:text-2xl tracking-[0.06em] leading-none uppercase drop-shadow-[0_1px_1px_rgba(250,244,228,0.6)]">QueryGoa</Link>
      <div className="hidden md:flex items-center gap-7">{LINKS.map((link) => <Link key={link.key} to={link.to} className={`${LINK_CLASSES} ${active === link.key ? "text-terracotta" : ""}`}>{link.label}</Link>)}</div>
      <div className="flex items-center gap-2.5"><IconButton name="search" label="Search" onClick={() => scrollTo("why")} /><IconButton name="user" label="Get started" onClick={() => scrollTo("cta")} /><IconButton name="menu" label="Menu" /></div>
    </nav>
  );
}

function scrollTo(id) {
  document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
}
