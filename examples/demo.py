"""Deterministic, keyless CatalystEdge demonstration."""

from __future__ import annotations

import json

from catalystedge import assess_level, event_readiness


def main() -> None:
    bars = [
        {"open": 779.5, "high": 779.8, "low": 779.3, "close": 779.7, "volume": 100},
        {"open": 779.7, "high": 779.9, "low": 779.5, "close": 779.8, "volume": 100},
        {"open": 780.1, "high": 780.5, "low": 780.05, "close": 780.3, "volume": 180},
        {"open": 780.3, "high": 780.6, "low": 780.2, "close": 780.4, "volume": 170},
        {"open": 780.4, "high": 780.7, "low": 780.3, "close": 780.5, "volume": 160},
    ]
    result = {
        "event": event_readiness(
            "us-midterm-2026-results-window",
            as_of="2026-11-04T03:00:00Z",
        ),
        "level": assess_level(
            bars,
            level=780,
            direction="above",
            level_name="demo decision rail",
            event_id="us-midterm-2026-results-window",
            as_of="2026-11-04T03:00:00Z",
        ),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
