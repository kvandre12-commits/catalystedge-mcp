---
name: catalystedge
description: Uses a separately installed CatalystEdge MCP server to inspect scheduled volatility windows, assess custom market levels, distinguish provisional crosses from accepted or rejected breaks, and check whether options evidence is complete. Use for CPI, FOMC, election, earnings, or other catalyst preparation without predicting direction or placing trades.
---

# CatalystEdge

## Purpose

Use CatalystEdge to answer two separate questions:

1. Is a scheduled event close enough to warrant volatility preparation?
2. Did price merely cross a user-supplied level, or did the auction show acceptance?

Never infer direction from an event. Never treat proximity to CPI, FOMC, earnings, or
an election as permission to buy or sell an option.

## Prerequisite

The user must separately install and configure the open-source CatalystEdge MCP server.
It runs locally over stdio. It needs no API key, broker, SharpEdge server, network
listener, or proprietary market-data subscription.

Do not invent prices or event dates. Level assessment requires OHLCV bars supplied by
the user or another authorized tool. A custom event remains unverified until its time
is checked against an authoritative source.

## Tools

### `upcoming_events`

List curated bundled events and their provenance.

```json
{"as_of":"2026-10-20T12:00:00Z","lookahead_days":15}
```

Optional `event_types` filters exact event-type strings. The catalog is curated, not a
complete economic or earnings calendar. Say so when presenting results.

### `event_readiness`

Assess one bundled event by its exact ID.

```json
{"event_id":"fomc-2026-10-28-statement","as_of":"2026-10-27T18:00:00Z"}
```

Possible decisions are `monitor`, `inspect_options`, `event_window_active`,
`post_event_reassess`, and `stand_down`. These are research states, not trade signals.

### `assess_event`

Assess a user-supplied CPI, earnings, election, or other event.

```json
{
  "title":"Consumer Price Index",
  "event_type":"cpi",
  "starts_at":"2026-11-12T08:30:00-05:00",
  "source_url":"https://www.bls.gov/schedule/news_release/cpi.htm",
  "as_of":"2026-11-11T14:00:00Z"
}
```

Custom events are always returned as unverified user input. A source URL supplies
provenance but does not prove CatalystEdge fetched or validated it.

### `assess_level`

Assess up to 500 chronological OHLCV bars around one positive level.

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

States are `no_test`, `testing`, `provisional`, `rejected`,
`accepted_unconfirmed`, and `confirmed`. Confirmation requires repeated closes plus a
held retest, expanded volume, or decisive displacement. Catalyst context never changes
the state by itself.

### `options_readiness`

Combine a bundled event lifecycle with an evidence checklist.

```json
{
  "event_id":"fomc-2026-10-28-statement",
  "implied_volatility_pct":40,
  "realized_volatility_pct":20,
  "implied_move_pct":3,
  "historical_event_move_pct":2,
  "bid_ask_width_pct":4,
  "days_to_expiration":7,
  "maximum_loss":250
}
```

The tool compares supplied values and reports missing evidence. It never recommends a
strategy, strike, side, size, or order, even when evidence is complete.

## Interpretation policy

- A wick is not acceptance.
- One close beyond a level is provisional.
- Repeated closes show acceptance, not guaranteed continuation.
- A held retest, participation expansion, or decisive displacement adds confirmation.
- `confirmed` is a deterministic heuristic state, not a probability of profit.
- Missing evidence stays missing; never replace it with a neutral value.
- Event timing can explain why participation may change, not which direction wins.
- Verify timestamps, timezone offsets, source freshness, and bar ordering.
- Clearly label bundled, custom, synthetic, stale, and unavailable inputs.

## Response format

Report:

1. event and source-verification status;
2. lifecycle phase and readiness decision;
3. level, direction, buffer, and state when bars are supplied;
4. supporting and contradicting evidence;
5. missing options evidence;
6. limitations and `trade_permission: false`.

Use restrained wording such as “the supplied bars show accepted trade above 780.” Do
not say “buy,” “sell,” “guaranteed,” “safe,” or “will break.”

## Security and financial boundary

CatalystEdge uses local stdio and performs no network requests. It has no credential,
broker, order-entry, portfolio, or autonomous-execution capability. Do not ask for API
keys. Do not read unrelated files or run shell commands on the skill's behalf.

CatalystEdge is research software, not personalized financial advice. The user remains
responsible for source verification, market-data rights, timestamps, liquidity,
maximum loss, and every financial decision.
