from catalystedge.service import MAX_BARS, assess_level


def bar(open_, high, low, close, volume=100):
    return {"open": open_, "high": high, "low": low, "close": close, "volume": volume}


def test_assess_level_attaches_but_does_not_obey_catalyst():
    result = assess_level(
        [bar(779.5, 779.8, 779.3, 779.7), bar(779.7, 780.5, 779.6, 780.4)],
        level=780,
        direction="above",
        event_id="us-midterm-2026-results-window",
        as_of="2026-11-04T03:00:00Z",
    )
    assert result["state"] == "provisional"
    assert result["confirmed"] is False
    assert result["catalyst"]["event"]["id"] == "us-midterm-2026-results-window"


def test_bar_fanout_is_bounded():
    try:
        assess_level(
            [bar(1, 1, 1, 1)] * (MAX_BARS + 1),
            level=1,
            direction="above",
        )
    except ValueError as exc:
        assert str(MAX_BARS) in str(exc)
    else:
        raise AssertionError("oversized bar input must fail")
