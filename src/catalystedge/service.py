"""Thin orchestration over CatalystEdge's pure engines."""

from __future__ import annotations

from typing import Any

from .events import custom_event_readiness, event_readiness, upcoming_events
from .level_break import Bar, assess_level_break
from .options import options_checklist

MAX_BARS = 500


def assess_level(
    bars: list[Bar],
    *,
    level: float,
    direction: str,
    level_name: str = "custom",
    event_id: str | None = None,
    as_of: str | None = None,
    acceptance_closes: int = 3,
    buffer_pct: float = 0.03,
) -> dict[str, Any]:
    """Assess one custom level and optionally attach bundled catalyst context."""
    if len(bars) > MAX_BARS:
        raise ValueError(f"bars is limited to {MAX_BARS} entries")
    catalyst = event_readiness(event_id, as_of=as_of) if event_id else None
    return assess_level_break(
        bars,
        level=level,
        direction=direction,  # type: ignore[arg-type]
        level_name=level_name,
        acceptance_closes=acceptance_closes,
        buffer_pct=buffer_pct,
        catalyst=catalyst,
    )


def options_readiness(event_id: str, *, as_of: str | None = None, **evidence: Any) -> dict[str, Any]:
    """Combine event lifecycle context with an options-evidence checklist."""
    event = event_readiness(event_id, as_of=as_of)
    checklist = options_checklist(**evidence)
    return {
        "schema": "catalystedge.options_readiness.v1",
        "event_readiness": event,
        "options_evidence": checklist,
        "decision": event["decision"],
        "analysis_status": checklist["status"],
        "trade_permission": False,
    }


__all__ = [
    "MAX_BARS",
    "assess_level",
    "custom_event_readiness",
    "event_readiness",
    "options_readiness",
    "upcoming_events",
]
