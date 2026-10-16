# CatalystEdge

**The catalyst is the clock. The level is the decision point. Price confirms the break.**

CatalystEdge is a local MCP server for explainable catalyst readiness and market-level
behavior. It separates two questions that are too often mashed into one bad trade:

1. Is a scheduled catalyst close enough to justify volatility research?
2. Did price merely cross a level, or did the auction accept beyond it?

It does not predict direction, fetch market data, select an option, connect to a broker,
or authorize a trade.

## What it does

- Lists a small, source-backed bundled catalyst catalog.
- Accepts custom CPI, earnings, election, and other event times as **unverified input**.
- Classifies event lifecycle as distant, preparation, pre-event, active, post-event, or resolved.
- Assesses up to 500 user-supplied OHLCV bars around any positive price level.
- Distinguishes `testing`, `provisional`, `rejected`, `accepted_unconfirmed`, and `confirmed`.
- Checks whether options evidence is complete without recommending a contract or strategy.
- Runs locally over MCP stdio with no API key or network request.

## Confirmation rule

A catalyst never upgrades a weak break. A confirmed level break requires repeated
closes beyond a configurable buffer plus at least one observable confirmation:

- a retest that touches the level area and holds;
- post-break volume at least 1.2× the pre-break median; or
- a decisive candle body closing near its directional extreme.

This is a deterministic heuristic state—not a calibrated probability of profit.

## Install

Requires Python 3.11 or newer.

```bash
git clone https://github.com/kvandre12-commits/catalystedge-mcp.git
cd catalystedge-mcp
python -m venv .venv
.venv/bin/python -m pip install -e .
```

On Windows, use `.venv\\Scripts\\python` instead of `.venv/bin/python`.

## Keyless demo

```bash
.venv/bin/python examples/demo.py
```

The demo uses fixed synthetic OHLCV bars and the bundled 2026 election-results window.
It performs no network request and must not be presented as live market analysis.

## MCP configuration

Use an absolute path in your MCP client's configuration:

```json
{
  "mcpServers": {
    "catalystedge": {
      "command": "/absolute/path/to/catalystedge-mcp/.venv/bin/python",
      "args": ["-m", "catalystedge.server"]
    }
  }
}
```

CatalystEdge uses stdio. It does not expose an HTTP port or require a SharpEdge server.

## MCP tools

### `upcoming_events`

Lists curated bundled catalysts in a bounded horizon.

```json
{"as_of":"2026-10-20T12:00:00Z","lookahead_days":15}
```

The response explicitly reports that this is not a complete market calendar.

### `event_readiness`

Assesses one bundled event by ID.

```json
{"event_id":"fomc-2026-10-28-statement","as_of":"2026-10-27T18:00:00Z"}
```

### `assess_event`

Assesses a user-supplied event without claiming CatalystEdge verified it.

```json
{
  "title":"Consumer Price Index",
  "event_type":"cpi",
  "starts_at":"2026-11-12T08:30:00-05:00",
  "source_url":"https://www.bls.gov/schedule/news_release/cpi.htm",
  "as_of":"2026-11-11T14:00:00Z"
}
```

### `assess_level`

Assesses supplied chronological OHLCV bars around one level.

```json
{
  "bars":[
    {"open":779.7,"high":780.5,"low":779.6,"close":780.3,"volume":180},
    {"open":780.3,"high":780.6,"low":780.2,"close":780.4,"volume":170},
    {"open":780.4,"high":780.7,"low":780.3,"close":780.5,"volume":160}
  ],
  "level":780,
  "direction":"above",
  "level_name":"decision rail"
}
```

### `options_readiness`

Checks event context and required user-supplied options evidence:

- implied volatility and a comparable realized-volatility measure;
- implied move and a comparable historical event move;
- bid-ask width;
- days to expiration;
- maximum defined loss.

Even complete evidence returns `trade_permission: false`.

## Event coverage and provenance

Version 0.1.1 deliberately bundles only a narrow, auditable catalog:

- October 28, 2026 FOMC statement;
- October 28, 2026 FOMC press conference;
- November 3–4, 2026 U.S. midterm election analytical results window.

The election date is official; the results-window timestamps are transparent analytical
boundaries because jurisdictions do not publish results on one universal schedule.
Release times should always be rechecked on event day. Custom events remain unverified
even when the caller supplies an official-looking URL.

CatalystEdge bundles no proprietary prices, options chains, earnings feed, or economic
database. Users are responsible for their right to provide data from another source.

## Output honesty

- Missing evidence is never converted to neutral evidence.
- Invalid timestamps, bars, numbers, or unknown event IDs return explicit errors.
- All timestamps must include timezone offsets.
- A wick is not acceptance.
- Repeated closes show acceptance, not guaranteed continuation.
- Event proximity means “inspect,” not “buy volatility.”
- No output is personalized financial advice.

## Development

```bash
.venv/bin/python -m pytest -q
.venv/bin/ruff check src tests examples
.venv/bin/python -m compileall -q src tests examples
```

The tests replay deterministic events and bars. They do not require credentials or
network access.

## License

MIT. Third-party event pages and user-supplied market data remain governed by their own
terms. CatalystEdge is an independent research project and is not affiliated with the
Federal Reserve, USA.gov, BLS, any exchange, broker, or data vendor.
