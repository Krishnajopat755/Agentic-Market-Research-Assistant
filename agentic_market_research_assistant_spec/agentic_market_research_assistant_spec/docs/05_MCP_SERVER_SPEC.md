# Finance MCP Server Specification

## 1. Purpose

Expose finance research capabilities through narrow, typed, auditable MCP tools.

MCP is the tool boundary, not the analytics implementation.

Target: MCP 2026-07-28 + official Python SDK v2.

## 2. Tool catalog

### Symbol/data
- `resolve_symbol`
- `fetch_market_snapshot`
- `fetch_historical_bars`
- `fetch_market_benchmark`
- `fetch_market_calendar`

### News
- `fetch_market_news`
- `normalize_and_deduplicate_news`

### Sentiment
- `compute_sentiment`
- `aggregate_news_sentiment`

### Technical
- `compute_technical_indicators`

### Research features/signal
- `build_research_features`
- `run_signal_model`
- `evaluate_signal_model_historical`
- `compare_signal_candidates`

### Evidence/report
- `get_research_evidence`
- `validate_report_claims`
- `render_daily_report`
- `persist_research_record`

### Operational
- `get_provider_health`
- `get_artifact_metadata`

## 3. Tool context

All calls should carry:
```json
{
  "run_id": "uuid",
  "analysis_timestamp": "RFC3339",
  "request_id": "uuid"
}
```

Side-effectful calls additionally require `idempotency_key`.

## 4. Authorization matrix

| Tool group | Market Data | Sentiment/Technical | Synthesis |
|---|---:|---:|---:|
| Symbol/market/news retrieval | ✓ |  |  |
| News normalization |  | ✓ |  |
| Sentiment |  | ✓ |  |
| Indicators/features |  | ✓ |  |
| Signal model |  | ✓ |  |
| Historical evaluation |  | ✓ |  |
| Evidence | read | read | ✓ |
| Report validation/render |  |  | ✓ |
| Persist research record |  |  | ✓ |

Server-side enforcement must verify role and workflow state.

## 5. Provider abstraction

```text
MarketDataProvider
  resolve_symbol()
  snapshot()
  historical_bars()
  benchmark()
  calendar()

NewsProvider
  news()
```

## 6. Error contract

```json
{
  "error_code": "RATE_LIMITED",
  "message": "Provider rate limit reached.",
  "retryable": true,
  "retry_after_seconds": 30,
  "trace_id": "..."
}
```

Possible codes:
- AUTH_ERROR
- RATE_LIMITED
- PROVIDER_UNAVAILABLE
- PROVIDER_SCHEMA_CHANGED
- INVALID_SYMBOL
- EMPTY_RESULT
- STALE_DATA
- INVALID_TIME_RANGE
- POINT_IN_TIME_VIOLATION
- TOOL_NOT_AUTHORIZED
- STATE_PRECONDITION_FAILED
- ARTIFACT_INTEGRITY_FAILED

## 7. Idempotency

Canonicalize inputs and hash them for side-effectful operations. Duplicate calls should return prior committed results rather than repeat expensive work.

## 8. No arbitrary tools

Never add:
- execute_python;
- execute_shell;
- browser navigation;
- arbitrary URL fetch;
- arbitrary SQL;
- unrestricted filesystem access;
- broker/order APIs.

## 9. Protocol notes

The 2026-07-28 MCP specification is stateless at protocol level, removing the old initialize/session handshake. Use the current SDK/protocol rather than legacy session assumptions.

References:
- https://blog.modelcontextprotocol.io/posts/2026-07-28/
- https://py.sdk.modelcontextprotocol.io/protocol-versions/
