import { CHUNKING_STRATEGIES } from "../../utils/constants";
import { useScrollAnimation } from "../../hooks/useScrollAnimation";
import Icon from "../Icon/Icon";

export default function Chunking() {
  const { ref, inView } = useScrollAnimation();

  return (
    <section id="chunking" className="px-margin-mobile md:px-margin-desktop py-16 bg-surface-container/40">
      <div className="max-w-5xl mx-auto" ref={ref}>
        <div className={`text-center mb-10 ${inView ? "staggered-item" : "staggered-item"}`} style={{ animationDelay: inView ? "0s" : "0s" }}>
          <span className="chip bg-surface-variant text-on-surface">CHUNKING</span>
          <h2 className="font-headline-lg text-headline-lg-mobile uppercase text-primary mt-4">
            Split right. Retrieve right.
          </h2>
          <p className="font-meta-mono text-meta-mono uppercase text-secondary mt-2">
            COMPARE STRATEGIES · TUNE · MEASURE HIT@K
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {CHUNKING_STRATEGIES.map((strategy, i) => (
            <article
              key={strategy.id}
              className="border border-outline-variant bg-surface rounded-lg p-5 hover:border-primary hover:offset-shadow-sm transition-all flex flex-col"
              style={{ transitionDelay: `${i * 40}ms` }}
            >
              <div className="w-10 h-10 rounded-lg bg-primary-container/15 text-primary flex items-center justify-center mb-3">
                <Icon name={strategy.icon} size={20} />
              </div>
              <h3 className="font-body-bold text-body-bold text-primary uppercase">{strategy.name}</h3>
              <span className="font-meta-mono text-meta-mono uppercase text-tertiary mb-2">
                {strategy.tagline}
              </span>
              <p className="font-body-md text-body-md text-on-surface-variant text-sm">{strategy.description}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
