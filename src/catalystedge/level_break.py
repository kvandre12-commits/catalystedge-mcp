"""Pure, deterministic evidence for a level-break assessment.

The engine does not predict returns. It separates a wick or first close beyond a
level from repeated auction acceptance, then asks whether participation,
displacement, or a held retest confirms that acceptance.
"""

from __future__ import annotations

from statistics import median
from typing import Literal, TypedDict

Direction = Literal["above", "below"]


class Bar(TypedDict):
    open: float
    high: float
    low: float
    close: float
    volume: float


def _validate_bars(bars: list[Bar]) -> None:
    if not bars:
        raise ValueError("bars must not be empty")
    for index, bar in enumerate(bars):
        missing = {"open", "high", "low", "close", "volume"} - bar.keys()
        if missing:
            raise ValueError(f"bar {index} is missing: {', '.join(sorted(missing))}")
        if bar["high"] < bar["low"]:
            raise ValueError(f"bar {index} high must be >= low")
        if not bar["low"] <= bar["open"] <= bar["high"]:
            raise ValueError(f"bar {index} open must be inside high/low")
        if not bar["low"] <= bar["close"] <= bar["high"]:
            raise ValueError(f"bar {index} close must be inside high/low")
        if bar["volume"] < 0:
            raise ValueError(f"bar {index} volume must be non-negative")


def _is_beyond(close: float, direction: Direction, upper: float, lower: float) -> bool:
    return close > upper if direction == "above" else close < lower


def _breached(bar: Bar, direction: Direction, upper: float, lower: float) -> bool:
    return bar["high"] > upper if direction == "above" else bar["low"] < lower


def _opposite(close: float, direction: Direction, upper: float, lower: float) -> bool:
    return close < lower if direction == "above" else close > upper


def _extension_pct(bars: list[Bar], level: float, direction: Direction) -> float:
    if direction == "above":
        extreme = max(bar["high"] for bar in bars)
        return max(0.0, (extreme - level) / level * 100)
    extreme = min(bar["low"] for bar in bars)
    return max(0.0, (level - extreme) / level * 100)


def _latest_displacement(bar: Bar, direction: Direction) -> dict[str, float | bool]:
    span = max(bar["high"] - bar["low"], 1e-12)
    body_ratio = abs(bar["close"] - bar["open"]) / span
    close_location = (bar["close"] - bar["low"]) / span
    directionally_closed = close_location >= 0.7 if direction == "above" else close_location <= 0.3
    return {
        "body_to_range": round(body_ratio, 4),
        "close_location": round(close_location, 4),
        "directionally_closed": directionally_closed,
        "decisive": body_ratio >= 0.6 and directionally_closed,
    }


def _held_retest(
    bars: list[Bar], first_close_index: int | None, direction: Direction, upper: float, lower: float
) -> bool:
    if first_close_index is None:
        return False
    for bar in bars[first_close_index + 1 :]:
        if direction == "above":
            touched = bar["low"] <= upper
            held = bar["close"] > upper
        else:
            touched = bar["high"] >= lower
            held = bar["close"] < lower
        if touched and held:
            return True
    return False


def _volume_ratio(bars: list[Bar], first_close_index: int | None) -> float | None:
    if first_close_index is None or first_close_index == 0:
        return None
    before = [bar["volume"] for bar in bars[:first_close_index] if bar["volume"] > 0]
    after = [bar["volume"] for bar in bars[first_close_index:] if bar["volume"] > 0]
    if not before or not after:
        return None
    baseline = median(before)
    if baseline <= 0:
        return None
    return round((sum(after) / len(after)) / baseline, 4)


def assess_level_break(
    bars: list[Bar],
    *,
    level: float,
    direction: Direction,
    level_name: str = "custom",
    acceptance_closes: int = 3,
    buffer_pct: float = 0.03,
    catalyst: dict[str, object] | None = None,
) -> dict[str, object]:
    """Assess observable acceptance around one user-supplied level.

    ``buffer_pct`` is a percentage, so 0.03 means three basis points. Catalyst
    metadata is preserved as context but never changes the confirmation state.
    """
    _validate_bars(bars)
    if level <= 0:
        raise ValueError("level must be positive")
    if direction not in {"above", "below"}:
        raise ValueError("direction must be 'above' or 'below'")
    if acceptance_closes < 2:
        raise ValueError("acceptance_closes must be at least 2")
    if not 0 <= buffer_pct <= 1:
        raise ValueError("buffer_pct must be between 0 and 1 percent")

    buffer = level * buffer_pct / 100
    upper, lower = level + buffer, level - buffer
    breach_indices = [
        index for index, bar in enumerate(bars) if _breached(bar, direction, upper, lower)
    ]
    beyond_indices = [
        index
        for index, bar in enumerate(bars)
        if _is_beyond(bar["close"], direction, upper, lower)
    ]
    first_close_index = beyond_indices[0] if beyond_indices else None
    recent = bars[-acceptance_closes:]
    accepted_close_count = sum(
        _is_beyond(bar["close"], direction, upper, lower) for bar in recent
    )
    latest_beyond = _is_beyond(bars[-1]["close"], direction, upper, lower)
    latest_opposite = _opposite(bars[-1]["close"], direction, upper, lower)
    accepted = len(recent) == acceptance_closes and accepted_close_count == acceptance_closes
    retest_held = _held_retest(bars, first_close_index, direction, upper, lower)
    volume_ratio = _volume_ratio(bars, first_close_index)
    displacement = _latest_displacement(bars[-1], direction)
    participation_expanded = volume_ratio is not None and volume_ratio >= 1.2
    confirming_behavior = retest_held or participation_expanded or bool(displacement["decisive"])

    if not breach_indices:
        state = "no_test"
    elif latest_opposite:
        state = "rejected"
    elif accepted and confirming_behavior:
        state = "confirmed"
    elif accepted:
        state = "accepted_unconfirmed"
    elif latest_beyond:
        state = "provisional"
    else:
        state = "testing"

    evidence = []
    if accepted:
        evidence.append(f"{acceptance_closes} consecutive closes accepted {direction} the buffer")
    elif latest_beyond:
        evidence.append("price closed beyond the buffer, but repeated acceptance is incomplete")
    if retest_held:
        evidence.append("a post-break retest touched the level area and held")
    if participation_expanded:
        evidence.append(f"post-break volume was {volume_ratio:.2f}x the pre-break median")
    if displacement["decisive"]:
        evidence.append("the latest candle displaced and closed near its directional extreme")
    if state == "rejected":
        evidence.append("price breached the level but closed through the opposite buffer")

    missing = []
    if volume_ratio is None:
        missing.append("pre-break volume baseline")
    if not catalyst:
        missing.append("verified catalyst context")

    return {
        "schema": "catalystedge.level_break.v1",
        "level": {"name": level_name, "price": level, "direction": direction, "buffer": buffer},
        "state": state,
        "confirmed": state == "confirmed",
        "trade_permission": False,
        "acceptance": {
            "required_closes": acceptance_closes,
            "accepted_close_count": accepted_close_count,
            "latest_beyond": latest_beyond,
        },
        "breach": {
            "observed": bool(breach_indices),
            "latest_index": breach_indices[-1] if breach_indices else None,
            "extension_pct": round(_extension_pct(bars, level, direction), 4),
        },
        "confirmation": {
            "held_retest": retest_held,
            "volume_ratio": volume_ratio,
            "participation_expanded": participation_expanded,
            "displacement": displacement,
        },
        "catalyst": catalyst or {"available": False},
        "evidence": evidence,
        "missing_evidence": missing,
        "limitations": [
            "heuristic state, not a calibrated probability",
            "catalyst context cannot confirm a break",
            "no trade or options-contract authorization",
        ],
    }
