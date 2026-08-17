"""Latency measurement helpers."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class LatencyStats:
    stages: dict[str, list[float]] = field(default_factory=dict)

    def add(self, stage: str, ms: float) -> None:
        self.stages.setdefault(stage, []).append(ms)

    def summary(self) -> dict[str, dict[str, float]]:
        out: dict[str, dict[str, float]] = {}
        for stage, vals in self.stages.items():
            arr = np.asarray(vals, dtype=np.float64)
            out[stage] = {
                "avg_ms": round(float(arr.mean()), 2),
                "p50_ms": round(float(np.percentile(arr, 50)), 2),
                "p95_ms": round(float(np.percentile(arr, 95)), 2),
                "p99_ms": round(float(np.percentile(arr, 99)), 2),
                "count": int(len(arr)),
            }
        return out

    @property
    def total_avg_ms(self) -> float:
        if not self.stages:
            return 0.0
        return round(float(np.mean([np.mean(v) for v in self.stages.values()])), 2)


def measure_latencies(latencies: list[float]) -> dict[str, float]:
    """Aggregate a single-stage latency series into p50/p95/p99/avg."""
    arr = np.asarray(latencies, dtype=np.float64)
    if len(arr) == 0:
        return {"avg_ms": 0.0, "p50_ms": 0.0, "p95_ms": 0.0, "p99_ms": 0.0, "count": 0}
    return {
        "avg_ms": round(float(arr.mean()), 2),
        "p50_ms": round(float(np.percentile(arr, 50)), 2),
        "p95_ms": round(float(np.percentile(arr, 95)), 2),
        "p99_ms": round(float(np.percentile(arr, 99)), 2),
        "count": int(len(arr)),
    }


__all__ = ["LatencyStats", "measure_latencies"]