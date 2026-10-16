import asyncio

from catalystedge.server import assess_event, event_readiness, mcp, upcoming_events

EXPECTED_TOOLS = {
    "assess_event",
    "assess_level",
    "event_readiness",
    "options_readiness",
    "upcoming_events",
}


def test_mcp_registry_matches_documented_tools():
    tools = asyncio.run(mcp.list_tools())
    assert {tool.name for tool in tools} == EXPECTED_TOOLS


def test_server_validation_returns_error_object():
    result = upcoming_events(as_of="not-a-date")
    assert "error" in result


def test_server_unknown_event_returns_error_object():
    result = event_readiness("unknown")
    assert result == {"error": "unknown event_id: unknown"}


def test_custom_event_server_tool_preserves_unverified_status():
    result = assess_event(
        title="Example earnings",
        event_type="earnings",
        starts_at="2026-10-27T16:05:00-04:00",
        as_of="2026-10-27T12:00:00-04:00",
    )
    assert result["source_verified"] is False
    assert result["trade_permission"] is False
