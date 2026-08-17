import { useMemo } from "react";

export default function Waveform({ active = false, level = 0.5, bars = 24, className = "" }) {
  const barHeights = useMemo(
    () => Array.from({ length: bars }, () => 0.25 + Math.random() * 0.75),
    [bars]
  );

  return (
    <div className={`flex items-end justify-center gap-1 h-16 ${className}`} aria-hidden="true">
      {barHeights.map((h, i) => {
        const animated = active ? h * (0.4 + level * 0.6) : h * 0.25;
        return (
          <div
            key={i}
            className={`w-1.5 rounded-full bg-surface ${active ? "wave-bar" : ""}`}
            style={{
              height: `${Math.min(1, animated) * 100}%`,
              animationDelay: `${i * 0.05}s`,
              animationDuration: `${0.7 + (i % 5) * 0.12}s`,
            }}
          />
        );
      })}
    </div>
  );
}
