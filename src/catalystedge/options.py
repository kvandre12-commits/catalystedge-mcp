"""Options-evidence completeness checks without contract recommendations."""

from __future__ import annotations

from typing import Any


def _positive(name: str, value: float | None, missing: list[str]) -> float | None:
    if value is None:
        missing.append(name)
        return None
    number = float(value)
    if number <= 0:
        raise ValueError(f"{name} must be positive")
    return number


def options_checklist(
    *,
    implied_volatility_pct: float | None = None,
    realized_volatility_pct: float | None = None,
    implied_move_pct: float | None = None,
    historical_event_move_pct: float | None = None,
    bid_ask_width_pct: float | None = None,
    days_to_expiration: int | None = None,
    maximum_loss: float | None = None,
) -> dict[str, Any]:
    """Report whether enough evidence exists for human options review.

    This function never selects a strategy or grants trade permission.
    """
    missing: list[str] = []
    iv = _positive("implied_volatility_pct", implied_volatility_pct, missing)
    rv = _positive("realized_volatility_pct", realized_volatility_pct, missing)
    implied_move = _positive("implied_move_pct", implied_move_pct, missing)
    historical_move = _positive(
        "historical_event_move_pct", historical_event_move_pct, missing
    )
    width = _positive("bid_ask_width_pct", bid_ask_width_pct, missing)
    dte = _positive("days_to_expiration", days_to_expiration, missing)
    max_loss = _positive("maximum_loss", maximum_loss, missing)

    iv_rv = round(iv / rv, 4) if iv is not None and rv is not None else None
    implied_historical = (
        round(implied_move / historical_move, 4)
        if implied_move is not None and historical_move is not None
        else None
    )
    observations = []
    if iv_rv is not None:
        if iv_rv >= 1.35:
            observations.append("implied volatility is materially above supplied realized volatility")
        elif iv_rv <= 0.85:
            observations.append("implied volatility is below supplied realized volatility")
        else:
            observations.append("implied and supplied realized volatility are broadly comparable")
    if implied_historical is not None:
        if implied_historical >= 1.25:
            observations.append("implied move exceeds the supplied historical event move")
        elif implied_historical <= 0.8:
            observations.append("implied move is below the supplied historical event move")
        else:
            observations.append("implied and supplied historical event moves are comparable")
    if width is not None and width > 10:
        observations.append("bid-ask width is large and may make execution quality poor")
    if dte is not None and dte < 1:
        observations.append("expiration timing is too close for this checklist")

    return {
        "schema": "catalystedge.options_checklist.v1",
        "status": "ready_for_human_review" if not missing else "insufficient_evidence",
        "evidence_complete": not missing,
        "trade_permission": False,
        "missing_evidence": missing,
        "ratios": {
            "iv_to_realized": iv_rv,
            "implied_to_historical_event_move": implied_historical,
        },
        "observations": observations,
        "supplied": {
            "bid_ask_width_pct": width,
            "days_to_expiration": dte,
            "maximum_loss": max_loss,
        },
        "limitations": [
            "comparisons depend on user-supplied values and measurement windows",
            "no strategy, strike, side, size, or order is recommended",
            "complete evidence still requires independent human judgment",
        ],
    }
