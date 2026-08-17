"""Benchmark routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from ..config.constants import DEMO_QUERIES
from ..models.request import BenchmarkRequest
from ..models.response import BenchmarkResult

router = APIRouter(prefix="/benchmark", tags=["benchmark"])


@router.get("", response_model=BenchmarkResult)
async def get_benchmark(request: Request) -> BenchmarkResult:
    try:
        report = request.app.state.benchmark_report
    except AttributeError:
        report = {}
    return BenchmarkResult(success=bool(report), run_at="", summary={}, report=report)


@router.post("", response_model=BenchmarkResult)
async def run_benchmark(request: Request, payload: BenchmarkRequest | None = None) -> BenchmarkResult:
    services = request.app.state.services
    queries = payload.queries if payload and payload.queries else DEMO_QUERIES
    top_k = payload.top_k if payload else None
    try:
        report = services.benchmark(queries, top_k)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"benchmark failed: {exc}") from exc
    request.app.state.benchmark_report = report
    summary = {
        "strategy": report.get("strategy"),
        "top_k": report.get("top_k"),
        "queries": report.get("queries"),
        "total_avg_ms": report.get("total_avg_ms"),
        "retrieve_p50_ms": report.get("latency", {}).get("retrieve", {}).get("p50_ms"),
    }
    return BenchmarkResult(success=True, run_at=report.get("run_at", ""), summary=summary, report=report)


__all__ = ["router"]