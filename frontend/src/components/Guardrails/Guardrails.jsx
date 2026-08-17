import { GUARDRAIL_NAMES } from "../../utils/constants";
import { useRAG } from "../../context/RAGContext";
import { useScrollAnimation } from "../../hooks/useScrollAnimation";
import Icon from "../Icon/Icon";

export default function Guardrails() {
  const { lastQuery } = useRAG();
  const { ref, inView } = useScrollAnimation();
  const checks = lastQuery?.guardrails?.checks || [];
  const passed = lastQuery?.guardrails?.passed;

  return (
    <section id="guardrails" className="px-margin-mobile md:px-margin-desktop py-16 bg-surface-container/40">
      <div className="max-w-5xl mx-auto" ref={ref}>
        <div className="text-center mb-10">
          <span className="chip bg-surface-variant text-on-surface">GUARDRAILS</span>
          <h2 className="font-headline-lg text-headline-lg-mobile uppercase text-primary mt-4">
            Grounded. Or nothing.
          </h2>
          <p className="font-meta-mono text-meta-mono uppercase text-secondary mt-2">
            SAFETY · RELEVANCE · GROUNDING · REFUSAL
          </p>
        </div>

        <div className={`grid grid-cols-2 lg:grid-cols-4 gap-4 ${inView ? "staggered-item" : "staggered-item"}`}>
          {GUARDRAIL_NAMES.map((guard) => {
            const check = checks.find((c) => c.name === guard.id);
            return (
              <article
                key={guard.id}
                className={`border-2 rounded-lg p-5 text-center transition-all ${
                  check
                    ? check.passed
                      ? "border-primary bg-primary-container/10"
                      : "border-error bg-error-container/20"
                    : "border-outline-variant bg-surface"
                }`}
              >
                <div
                  className={`w-12 h-12 mx-auto rounded-full flex items-center justify-center mb-3 ${
                    check
                      ? check.passed
                        ? "bg-primary text-on-primary"
                        : "bg-error text-on-error"
                      : "bg-surface-container-highest text-on-surface-variant"
                  }`}
                >
                  <Icon name={check ? (check.passed ? "check" : "close") : guard.icon} size={22} />
                </div>
                <h3 className="font-body-bold text-body-bold uppercase text-on-surface">{guard.label}</h3>
                <p className="font-meta-mono text-meta-mono uppercase mt-1 text-on-surface-variant min-h-[2em]">
                  {check ? (check.passed ? "passed" : "blocked") : "idle"}
                </p>
                {check && (
                  <p className="font-meta-mono text-meta-mono text-xs mt-2 text-secondary">
                    {check.reason}
                  </p>
                )}
              </article>
            );
          })}
        </div>

        {lastQuery && (
          <p className="mt-6 text-center font-meta-mono text-meta-mono uppercase">
            Last answer:{" "}
            <span className={passed ? "text-primary" : "text-error"}>
              {passed ? "all guardrails passed" : "guardrail failed"}
            </span>
          </p>
        )}
      </div>
    </section>
  );
}
