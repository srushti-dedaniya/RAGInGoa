import { useEffect, useState } from "react";
import { ragService } from "../../services/ragService";
import { formatLatency } from "../../utils/formatLatency";

export default function Benchmark() {
  const [report, setReport] = useState(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    ragService.getBenchmark().then((data) => setReport(data.report || null));
  }, []);

  const run = async () => {
    setRunning(true);
    setError(null);
    try {
      const data = await ragService.runBenchmark();
      setReport(data.report || null);
    } catch (err) {
      setError(err.message || "benchmark failed");
    } finally {
      setRunning(false);
    }
  };

  const stages = report?.latency || {};

  return (
    <section id="performance" className="px-margin-mobile md:px-margin-desktop py-16">
      <div className="max-w-5xl mx-auto">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-10">
          <div>
            <span className="chip font-dm-sans bg-sand/60 text-sea-deep border-sea/30">PERFORMANCE</span>
            <h2 className="font-display-serif italic font-semibold text-sea mt-4 text-4xl md:text-5xl leading-tight">
              Latency. Measured.
            </h2>
            <p className="font-dm-sans text-[12px] font-medium uppercase tracking-[0.08em] text-sea-deep/70 mt-2">
              DEV BENCHMARK · P50 / P95 / P99 · REPRODUCIBLE
            </p>
          </div>
          <button
            type="button"
            onClick={run}
            disabled={running}
            className="bg-terracotta text-paper font-dm-sans text-[12.5px] font-medium uppercase tracking-[0.08em] px-6 py-3 border-2 border-sea-deep shadow-[3px_3px_0_0_#0A3E35] hover:translate-x-[1px] hover:translate-y-[1px] hover:shadow-[1px_1px_0_0_#0A3E35] transition-all disabled:opacity-40 disabled:cursor-wait"
          >
            {running ? "Running…" : "Run benchmark"}
          </button>
        </div>

        {error && (
          <p className="mb-6 font-dm-sans text-[13px] text-error">{error}</p>
        )}

        {!report ? (
          <div className="border border-dotted border-sea rounded-xl p-8 text-center font-dm-sans text-[12px] font-medium uppercase tracking-[0.08em] text-sea-deep/70">
            No benchmark data yet — hit “Run benchmark”.
          </div>
        ) : (
          <div className="space-y-6">
            <div className="flex flex-wrap gap-3">
              <StatChip label="strategy" value={report.strategy} />
              <StatChip label="top_k" value={report.top_k} />
              <StatChip label="queries" value={report.queries} />
              <StatChip label="index size" value={report.index_size} />
              <StatChip label="total avg" value={formatLatency(report.total_avg_ms, 2)} highlight />
            </div>

            <div className="overflow-x-auto border border-sea/20 rounded-lg">
              <table className="w-full text-left font-dm-sans text-[13px]">
                <thead className="bg-sea text-paper uppercase tracking-[0.08em]">
                  <tr>
                    <th className="px-4 py-3">Stage</th>
                    <th className="px-4 py-3 text-right">avg</th>
                    <th className="px-4 py-3 text-right">p50</th>
                    <th className="px-4 py-3 text-right">p95</th>
                    <th className="px-4 py-3 text-right">p99</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-sea/20">
                  {Object.entries(stages).map(([stage, stats]) => (
                    <tr key={stage} className="bg-paper">
                      <td className="px-4 py-3 uppercase text-sea">{stage}</td>
                      <td className="px-4 py-3 text-right">{formatLatency(stats.avg_ms, 2)}</td>
                      <td className="px-4 py-3 text-right">{formatLatency(stats.p50_ms, 2)}</td>
                      <td className="px-4 py-3 text-right">{formatLatency(stats.p95_ms, 2)}</td>
                      <td className="px-4 py-3 text-right">{formatLatency(stats.p99_ms, 2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}

function StatChip({ label, value, highlight = false }) {
  return (
    <span
      className={`chip font-dm-sans ${
        highlight ? "bg-sea text-paper border-sea" : "bg-paper text-sea-deep border-sea/30"
      }`}
    >
      {label}: <strong>{value ?? "—"}</strong>
    </span>
  );
}