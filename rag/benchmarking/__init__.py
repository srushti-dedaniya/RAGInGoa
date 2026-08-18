"""Benchmarking utilities for RAGInGoa."""

from rag.benchmarking.benchmark import run_benchmark
from rag.benchmarking.latency import LatencyStats, measure_latencies

__all__ = ["run_benchmark", "LatencyStats", "measure_latencies"]
