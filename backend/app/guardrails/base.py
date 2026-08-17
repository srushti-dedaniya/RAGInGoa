"""Shared guardrail primitives."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Result:
    name: str
    passed: bool
    reason: str = ""
    score: float = 0.0

    def as_dict(self) -> dict:
        return {"name": self.name, "passed": self.passed, "reason": self.reason, "score": self.score}


__all__ = ["Result"]