"""CatalystEdge MCP server using local stdio transport."""

from __future__ import annotations

from typing import Any

try:  # mcp >= 2
    from mcp.server.mcpserver import MCPServer as _Server
except ImportError:  # pragma: no cover - mcp 1.x
    from mcp.server.fastmcp import FastMCP as _Server

from .service import assess_level as _assess_level
from .service import custom_event_readiness as _custom_event_readiness
from .service import event_readiness as _event_readiness
from .service import options_readiness as _options_readiness
from .service import upcoming_events as _upcoming_events

mcp = _Server(
    "CatalystEdge",
    instructions=(
        "CatalystEdge identifies scheduled volatility windows and explains whether price "
        "is testing, rejecting, or accepting beyond a user-supplied level. A catalyst "
        "never confirms a break. Outputs are research receipts, not trade permission."
    ),
)


def _error(exc: ValueError) -> dict[str, str]:
    return {"error": str(exc)}


@mcp.tool()
def upcoming_events(
    as_of: str | None = None,
    lookahead_days: int = 30,
    event_types: list[str] | None = None,
) -> dict[str, Any]:
    """List curated upcoming catalysts with exact source and coverage limitations."""
    try:
        return _upcoming_events(
            as_of=as_of,
            lookahead_days=lookahead_days,
            event_types=event_types,
        )
    except ValueError as exc:
        return _error(exc)


@mcp.tool()
def event_readiness(event_id: str, as_of: str | None = None) -> dict[str, Any]:
    """Classify one catalyst as distant, preparation, pre-event, active, or resolved."""
    try:
        return _event_readiness(event_id, as_of=as_of)
    except ValueError as exc:
        return _error(exc)


@mcp.tool()
def assess_event(
    title: str,
    event_type: str,
    starts_at: str,
    ends_at: str | None = None,
    importance: str = "high",
    breadth: str = "unknown",
    source_url: str | None = None,
    as_of: str | None = None,
) -> dict[str, Any]:
    """Assess a user-supplied CPI, earnings, election, or other event as unverified."""
    try:
        return _custom_event_readiness(
            title=title,
            event_type=event_type,
            starts_at=starts_at,
            ends_at=ends_at,
            importance=importance,
            breadth=breadth,
            source_url=source_url,
            as_of=as_of,
        )
    except ValueError as exc:
        return _error(exc)


@mcp.tool()
def assess_level(
    bars: list[dict[str, float]],
    level: float,
    direction: str,
    level_name: str = "custom",
    event_id: str | None = None,
    as_of: str | None = None,
    acceptance_closes: int = 3,
    buffer_pct: float = 0.03,
) -> dict[str, Any]:
    """Explain a break, rejection, or test at a custom level from supplied OHLCV bars."""
    try:
        return _assess_level(
            bars,  # type: ignore[arg-type]
            level=level,
            direction=direction,
            level_name=level_name,
            event_id=event_id,
            as_of=as_of,
            acceptance_closes=acceptance_closes,
            buffer_pct=buffer_pct,
        )
    except ValueError as exc:
        return _error(exc)


@mcp.tool()
def options_readiness(
    event_id: str,
    as_of: str | None = None,
    implied_volatility_pct: float | None = None,
    realized_volatility_pct: float | None = None,
    implied_move_pct: float | None = None,
    historical_event_move_pct: float | None = None,
    bid_ask_width_pct: float | None = None,
    days_to_expiration: int | None = None,
    maximum_loss: float | None = None,
) -> dict[str, Any]:
    """Check whether event and options evidence are complete enough for human review."""
    try:
        return _options_readiness(
            event_id,
            as_of=as_of,
            implied_volatility_pct=implied_volatility_pct,
            realized_volatility_pct=realized_volatility_pct,
            implied_move_pct=implied_move_pct,
            historical_event_move_pct=historical_event_move_pct,
            bid_ask_width_pct=bid_ask_width_pct,
            days_to_expiration=days_to_expiration,
            maximum_loss=maximum_loss,
        )
    except ValueError as exc:
        return _error(exc)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
