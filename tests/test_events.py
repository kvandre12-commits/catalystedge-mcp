from catalystedge.events import (
    custom_event_readiness,
    event_readiness,
    get_event,
    parse_datetime,
    upcoming_events,
)


def test_catalog_event_is_source_backed():
    event = get_event("fomc-2026-10-28-statement")
    assert event["source"]["authority"].startswith("Board of Governors")
    assert event["starts_at_utc"] == "2026-10-28T18:00:00Z"


def test_upcoming_events_is_bounded_and_honest_about_coverage():
    result = upcoming_events(as_of="2026-10-20T12:00:00Z", lookahead_days=15)
    assert result["count"] == 3
    assert result["coverage"]["complete_market_calendar"] is False


def test_upcoming_events_can_filter_types():
    result = upcoming_events(
        as_of="2026-10-20T12:00:00Z",
        lookahead_days=15,
        event_types=["election_results"],
    )
    assert [event["id"] for event in result["events"]] == [
        "us-midterm-2026-results-window"
    ]


def test_fomc_enters_inspection_window_without_trade_permission():
    result = event_readiness(
        "fomc-2026-10-28-statement",
        as_of="2026-10-27T18:00:00Z",
    )
    assert result["decision"] == "inspect_options"
    assert result["trade_permission"] is False


def test_election_window_becomes_active():
    result = event_readiness(
        "us-midterm-2026-results-window",
        as_of="2026-11-04T03:00:00Z",
    )
    assert result["phase"]["phase"] == "active"
    assert result["decision"] == "event_window_active"


def test_custom_cpi_event_is_supported_but_never_claimed_as_verified():
    result = custom_event_readiness(
        title="Consumer Price Index",
        event_type="cpi",
        starts_at="2026-11-12T08:30:00-05:00",
        source_url="https://www.bls.gov/schedule/news_release/cpi.htm",
        as_of="2026-11-11T14:00:00Z",
    )
    assert result["decision"] == "inspect_options"
    assert result["source_verified"] is False
    assert "not independently verified" in result["rationale"][-1]


def test_naive_datetime_is_rejected():
    try:
        parse_datetime("2026-11-03T18:00:00")
    except ValueError as exc:
        assert "timezone" in str(exc)
    else:
        raise AssertionError("naive timestamp must fail")


def test_unknown_event_is_an_error_not_neutral_output():
    try:
        get_event("made-up-catalyst")
    except ValueError as exc:
        assert "unknown event_id" in str(exc)
    else:
        raise AssertionError("unknown event must fail")
