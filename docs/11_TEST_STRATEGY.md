# Test Strategy

## 1. Unit tests

Provider normalization:
- schema mapping;
- timestamp normalization;
- missing fields.

News:
- URL canonicalization;
- duplicate detection;
- time cutoff;
- attribution.

Indicators:
- SMA/EMA/RSI/MACD reference calculations;
- warm-up NaNs;
- future-row exclusion.

Sentiment:
- deterministic fixtures;
- model versioning;
- input limits.

Signal:
- scorecard math;
- thresholds;
- feature-order stability;
- model serialization.

## 2. Point-in-time tests

- future row cannot affect current features;
- future news cannot affect current sentiment;
- unfinished intraday bar excluded;
- walk-forward splits remain chronological;
- future labels never become features.

## 3. MCP contract tests

For every tool:
- discovery;
- valid schema;
- invalid schema;
- typed error;
- authorization;
- state precondition;
- idempotency;
- trace context.

Critical:
Synthesis Agent cannot call raw news/market retrieval tools.

## 4. Provider tests

CI uses fixtures, not live APIs. Fixtures cover success, pagination, 429, outage, schema drift, duplicate news, empty results, and stale timestamps.

## 5. Agent tests

Use a fake LLM. Verify structured outputs, bounded retries, forbidden-tool rejection, evidence references, and absence of credentials in prompts.

## 6. Integration

Use Postgres, MinIO, MLflow, MCP, orchestrator, fake provider, and fake LLM. Test single-symbol, multi-symbol, failure recovery, and resume.

## 7. E2E

- AAPL fixture run;
- AAPL/MSFT/NVDA watchlist fixture run;
- generated reports;
- evidence map;
- signal artifact;
- traces;
- persisted research run.

## 8. Security tests

- article prompt injection;
- URL injection;
- path traversal;
- secret redaction;
- rate-limit flood;
- oversized articles/symbol lists;
- unauthorized tool call;
- future-data fixture.

## 9. CI

PR:
```text
ruff
mypy
pytest unit/contract/timepoint
coverage
```

Main:
- integration;
- Docker build;
- E2E;
- security.

Optional scheduled workflow:
- real provider smoke test with a dedicated key.
