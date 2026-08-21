export default function Footer() {
  return (
    <footer
      id="team"
      className="w-full bottom-0 bg-cream border-t border-sea/20 mt-20 flex flex-col md:flex-row justify-between items-center px-margin-mobile md:px-margin-desktop py-gutter"
    >
      <div className="font-label-caps text-label-caps text-sea-deep uppercase mb-4 md:mb-0">
        HH Goa 2026
      </div>
      <div className="font-meta-mono text-meta-mono uppercase text-sea-deep/80">LESS NOISE. MORE SIGNAL.</div>
      <div className="font-meta-mono text-meta-mono uppercase text-sea-deep/80">SYSTEM V.1.0</div>
    </footer>
  );
}
