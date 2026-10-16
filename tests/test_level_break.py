from catalystedge import assess_level_break


def bar(open_, high, low, close, volume=100):
    return {"open": open_, "high": high, "low": low, "close": close, "volume": volume}


def test_wick_and_rejection_is_not_a_real_break():
    result = assess_level_break(
        [
            bar(779.5, 779.8, 779.3, 779.7),
            bar(779.7, 780.8, 779.6, 780.1, 150),
            bar(780.1, 780.2, 778.9, 779.0, 180),
        ],
        level=780,
        direction="above",
    )
    assert result["state"] == "rejected"
    assert result["confirmed"] is False


def test_one_close_beyond_is_only_provisional():
    result = assess_level_break(
        [
            bar(779.4, 779.8, 779.2, 779.7),
            bar(779.7, 780.5, 779.6, 780.4, 130),
        ],
        level=780,
        direction="above",
    )
    assert result["state"] == "provisional"


def test_three_closes_without_confirmation_are_not_overclaimed():
    result = assess_level_break(
        [
            bar(779.6, 779.9, 779.4, 779.8),
            bar(780.3, 780.5, 780.25, 780.32),
            bar(780.32, 780.5, 780.28, 780.35),
            bar(780.35, 780.5, 780.30, 780.38),
        ],
        level=780,
        direction="above",
    )
    assert result["state"] == "accepted_unconfirmed"
    assert result["confirmed"] is False


def test_acceptance_plus_expanding_volume_confirms():
    result = assess_level_break(
        [
            bar(779.5, 779.8, 779.3, 779.7, 100),
            bar(779.7, 779.9, 779.5, 779.8, 100),
            bar(780.1, 780.5, 780.05, 780.3, 180),
            bar(780.3, 780.6, 780.2, 780.4, 170),
            bar(780.4, 780.7, 780.3, 780.5, 160),
        ],
        level=780,
        direction="above",
    )
    assert result["state"] == "confirmed"
    assert result["confirmation"]["participation_expanded"] is True


def test_held_retest_confirms_without_volume_expansion():
    result = assess_level_break(
        [
            bar(779.5, 779.8, 779.3, 779.7),
            bar(780.1, 780.5, 780.05, 780.3),
            bar(780.3, 780.45, 780.1, 780.35),
            bar(780.35, 780.5, 780.0, 780.4),
        ],
        level=780,
        direction="above",
    )
    assert result["state"] == "confirmed"
    assert result["confirmation"]["held_retest"] is True


def test_catalyst_never_upgrades_an_unaccepted_break():
    result = assess_level_break(
        [bar(779.5, 779.8, 779.3, 779.7), bar(779.7, 780.4, 779.6, 780.3)],
        level=780,
        direction="above",
        catalyst={"available": True, "type": "midterm_election", "days_to": 1},
    )
    assert result["state"] == "provisional"
    assert result["confirmed"] is False


def test_breakdown_direction_is_symmetric():
    result = assess_level_break(
        [
            bar(780.5, 780.7, 780.3, 780.4, 100),
            bar(779.9, 780.0, 779.4, 779.6, 180),
            bar(779.6, 779.8, 779.3, 779.5, 170),
            bar(779.5, 779.7, 779.2, 779.3, 160),
        ],
        level=780,
        direction="below",
    )
    assert result["state"] == "confirmed"


def test_invalid_bar_is_rejected_honestly():
    try:
        assess_level_break(
            [bar(9, 8, 9, 8.5)],
            level=9,
            direction="above",
        )
    except ValueError as exc:
        assert "high must be >= low" in str(exc)
    else:
        raise AssertionError("invalid bar must fail")
