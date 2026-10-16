# CatalystEdge Security and Permissions Declaration

## Marketplace package

The customer-facing ZIP contains one top-level `catalystedge/` directory with only
`SKILL.md` and `LICENSE`. Both are plain UTF-8 text with mode 0644. It contains no
executable, script, binary, symlink, hidden file, dependency installer, credential,
market-data payload, or obfuscated content.

## Server behavior

The separately installed open-source MCP server:

- uses local stdio transport;
- opens no network listener;
- performs no network request;
- reads only its bundled event catalog;
- accepts event metadata, OHLCV bars, levels, and options metrics supplied in tool calls;
- writes no customer data;
- uses no environment variable, API key, browser, shell command, or broker.

## Financial boundary

All tools return research evidence. Event timing never predicts direction. A catalyst
never confirms a break. Complete options evidence never changes `trade_permission`
from false. No tool selects a strategy, contract, strike, side, position size, or order.

## Data boundary

The bundled catalog is curated and explicitly not a complete market calendar. Custom
events are labeled unverified. No proprietary market data is bundled or fetched.
Users remain responsible for rights to any bars or options metrics supplied by another
tool or data provider.
