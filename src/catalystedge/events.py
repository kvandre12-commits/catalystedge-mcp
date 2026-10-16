"""Catalyst catalog and event-lifecycle calculations."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from importlib.resources import files
from typing import Any

_MAX_LOOKAHEAD_DAYS = 366


def parse_datetime(value: str | datetime | None, *, default_now: bool = False) -> datetime:
    """Parse an aware ISO-8601 datetime and normalize it to UTC."""
    if value is None:
        if default_now:
            return datetime.now(UTC)
        raise ValueError("datetime is required")
    if isinstance(value, datetime):
        parsed = value
    else:
        normalized = value.strip().replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError as exc:
            raise ValueError(f"invalid ISO-8601 datetime: {value}") from exc
    if parsed.tzinfo is None:
        raise ValueError("datetime must include a timezone offset")
    return parsed.astimezone(UTC)


def load_catalog() -> dict[str, Any]:
    """Load the bundled, reviewable event catalog."""
    path = files("catalystedge").joinpath("data/events.json")
    return json.loads(path.read_text(encoding="utf-8"))


def _normalized_event(event: dict[str, Any]) -> dict[str, Any]:
    start = parse_datetime(str(event["starts_at"]))
    end = parse_datetime(str(event["ends_at"]))
    if end < start:
        raise ValueError(f"event {event.get('id')} ends before it starts")
    return {
        **event,
        "starts_at_utc": start.isoformat().replace("+00:00", "Z"),
        "ends_at_utc": end.isoformat().replace("+00:00", "Z"),
    }


def catalog_events() -> list[dict[str, Any]]:
    """Return validated events sorted by start time."""
    events = [_normalized_event(event) for event in load_catalog().get("events", [])]
    ids = [str(event.get("id") or "") for event in events]
    if not all(ids) or len(ids) != len(set(ids)):
        raise ValueError("event catalog IDs must be present and unique")
    return sorted(events, key=lambda event: parse_datetime(event["starts_at"]))


def get_event(event_id: str) -> dict[str, Any]:
    """Return one bundled event or raise a clear validation error."""
    for event in catalog_events():
        if event["id"] == event_id:
            return event
    raise ValueError(f"unknown event_id: {event_id}")


def upcoming_events(
    *,
    as_of: str | datetime | None = None,
    lookahead_days: int = 30,
    event_types: list[str] | None = None,
) -> dict[str, Any]:
    """Return bundled events whose windows overlap the requested horizon."""
    if not 0 <= lookahead_days <= _MAX_LOOKAHEAD_DAYS:
        raise ValueError(f"lookahead_days must be between 0 and {_MAX_LOOKAHEAD_DAYS}")
    anchor = parse_datetime(as_of, default_now=True)
    horizon = anchor + timedelta(days=lookahead_days)
    allowed = {item.strip() for item in (event_types or []) if item.strip()}
    selected = []
    for event in catalog_events():
        start = parse_datetime(event["starts_at"])
        end = parse_datetime(event["ends_at"])
        if end < anchor or start > horizon:
            continue
        if allowed and event["type"] not in allowed:
            continue
        selected.append(event)
    return {
        "schema": "catalystedge.upcoming_events.v1",
        "as_of": anchor.isoformat().replace("+00:00", "Z"),
        "lookahead_days": lookahead_days,
        "count": len(selected),
        "events": selected,
        "coverage": {
            "bundled_types": sorted({event["type"] for event in catalog_events()}),
            "complete_market_calendar": False,
            "warning": "Bundled events are curated, not a complete economic or earnings calendar.",
        },
    }


def event_phase(event: dict[str, Any], *, as_of: str | datetime | None = None) -> dict[str, Any]:
    """Classify an event as distant, preparation, active, or post-event."""
    anchor = parse_datetime(as_of, default_now=True)
    start = parse_datetime(event["starts_at"])
    end = parse_datetime(event["ends_at"])
    hours_to_start = (start - anchor).total_seconds() / 3600
    hours_from_end = (anchor - end).total_seconds() / 3600
    if anchor < start:
        if hours_to_start <= 72:
            phase, decision = "pre_event", "inspect_options"
        elif hours_to_start <= 24 * 7:
            phase, decision = "preparation", "monitor"
        else:
            phase, decision = "distant", "monitor"
    elif anchor <= end:
        phase, decision = "active", "event_window_active"
    elif hours_from_end <= 24:
        phase, decision = "post_event", "post_event_reassess"
    else:
        phase, decision = "resolved", "stand_down"
    return {
        "phase": phase,
        "decision": decision,
        "hours_to_start": round(hours_to_start, 2),
        "hours_from_end": round(hours_from_end, 2),
    }


def _readiness_for_event(
    event: dict[str, Any],
    *,
    as_of: str | datetime | None,
    source_verified: bool,
) -> dict[str, Any]:
    phase = event_phase(event, as_of=as_of)
    rationale = [
        f"{event['title']} is classified as {event['importance']} importance.",
        f"Current lifecycle phase: {phase['phase']}.",
    ]
    if phase["decision"] == "inspect_options":
        rationale.append("Event proximity warrants inspecting volatility pricing and liquidity.")
    elif phase["decision"] == "event_window_active":
        rationale.append("The catalyst window is active; spreads and realized volatility may expand.")
    if not source_verified:
        rationale.append("The event source is not independently verified by CatalystEdge.")
    return {
        "schema": "catalystedge.event_readiness.v1",
        "event": event,
        "phase": phase,
        "decision": phase["decision"],
        "source_verified": source_verified,
        "trade_permission": False,
        "rationale": rationale,
        "required_options_evidence": [
            "event-expiry implied volatility",
            "implied move",
            "recent or event-conditioned realized move",
            "bid-ask quality and liquidity",
            "expiration relative to event",
            "maximum defined loss",
        ],
        "limitations": [
            "event timing does not predict direction",
            "event proximity does not prove volatility is underpriced",
            "no order or contract is authorized",
        ],
    }


def event_readiness(event_id: str, *, as_of: str | datetime | None = None) -> dict[str, Any]:
    """Build an evidence-first receipt for one bundled event."""
    event = get_event(event_id)
    source = event.get("source") or {}
    verified = str(source.get("verification") or "").startswith("official")
    return _readiness_for_event(event, as_of=as_of, source_verified=verified)


def custom_event_readiness(
    *,
    title: str,
    event_type: str,
    starts_at: str,
    ends_at: str | None = None,
    importance: str = "high",
    breadth: str = "unknown",
    source_url: str | None = None,
    as_of: str | datetime | None = None,
) -> dict[str, Any]:
    """Assess a user-supplied CPI, earnings, election, or other event.

    Custom events are deliberately labeled unverified. Supplying an official-looking
    URL is provenance context, not proof that CatalystEdge independently checked it.
    """
    if not title.strip() or not event_type.strip():
        raise ValueError("title and event_type are required")
    if importance not in {"low", "medium", "high"}:
        raise ValueError("importance must be low, medium, or high")
    end_value = ends_at or starts_at
    event = _normalized_event(
        {
            "id": "user-supplied-event",
            "type": event_type.strip(),
            "title": title.strip(),
            "starts_at": starts_at,
            "ends_at": end_value,
            "importance": importance,
            "breadth": breadth,
            "affected_symbols": [],
            "source": {
                "authority": "user supplied",
                "url": source_url,
                "verification": "unverified_user_input",
            },
            "notes": "User-supplied event; verify timing against an authoritative source.",
        }
    )
    return _readiness_for_event(event, as_of=as_of, source_verified=False)
