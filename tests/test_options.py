from catalystedge.options import options_checklist
from catalystedge.service import options_readiness


def test_missing_options_evidence_is_explicit():
    result = options_checklist(implied_volatility_pct=30)
    assert result["status"] == "insufficient_evidence"
    assert "realized_volatility_pct" in result["missing_evidence"]
    assert result["trade_permission"] is False


def test_complete_evidence_remains_human_review_only():
    result = options_checklist(
        implied_volatility_pct=40,
        realized_volatility_pct=20,
        implied_move_pct=3,
        historical_event_move_pct=2,
        bid_ask_width_pct=4,
        days_to_expiration=7,
        maximum_loss=250,
    )
    assert result["status"] == "ready_for_human_review"
    assert result["ratios"]["iv_to_realized"] == 2
    assert result["trade_permission"] is False


def test_invalid_numeric_evidence_fails_instead_of_becoming_missing():
    try:
        options_checklist(implied_volatility_pct=-1)
    except ValueError as exc:
        assert "must be positive" in str(exc)
    else:
        raise AssertionError("negative volatility must fail")


def test_combined_options_readiness_preserves_event_decision():
    result = options_readiness(
        "fomc-2026-10-28-statement",
        as_of="2026-10-27T18:00:00Z",
    )
    assert result["decision"] == "inspect_options"
    assert result["analysis_status"] == "insufficient_evidence"
    assert result["trade_permission"] is False
