# Agentic Market Research Assistant

Industry-style, portfolio-ready multi-agent finance research system that collects market/news data through API-backed MCP tools, performs sentiment + technical analysis, computes a bounded quantitative research signal, and generates an evidence-linked daily market research report.

## Core idea

```text
User / Scheduler
       |
       v
Orchestrator
       |
       +--> Market Data Agent
       |       |
       |       +--> MCP: market/news tools
       |
       +--> Sentiment & Technical Agent
       |       |
       |       +--> MCP: sentiment/indicator/feature tools
       |
       +--> Synthesis & Report Agent
               |
               +--> MCP: evidence/report tools
       |
       v
Daily Research Report + Signal
```

Runtime agents reason about research tasks. Actual data retrieval, normalization, indicator calculation, feature generation, scoring, and report persistence happen through typed, auditable MCP tools.

## Product boundaries

This is a **research assistant**, not an automated execution system.

It must:
- never place trades;
- never submit orders;
- never connect to a brokerage account in v1;
- timestamp every observation;
- distinguish source publication time from ingestion time;
- preserve original source URLs/IDs;
- detect stale/incomplete data;
- prevent look-ahead bias in historical backtests;
- show evidence behind every material conclusion.

A report may contain a quantitative market-state or directional research signal, but it must clearly label methodology, uncertainty, data freshness, and its non-personalized research purpose.

## Default provider strategy

Implement a provider interface rather than coupling the application to one API.

Recommended initial adapter:
- Alpha Vantage for daily equity time series, news/sentiment, and technical-indicator endpoints.

Alternative adapter:
- Polygon/Massive for market news and market snapshots where the account/licence supports them.

Provider capabilities differ by plan, market, entitlement, and endpoint. Do not hard-code assumptions about real-time access or quota limits.

## Technology baseline

- Python 3.11+
- uv
- Pydantic / pydantic-settings
- Pandas / NumPy
- scikit-learn
- optional PyTorch for LSTM sequence model
- sentiment adapter (lexicon baseline and/or finance transformer)
- LangGraph
- official MCP Python SDK v2
- Anthropic API provider adapter
- MLflow
- PostgreSQL
- MinIO/S3
- FastAPI
- OpenTelemetry
- structlog
- pytest / pytest-asyncio / pytest-cov
- Ruff / mypy
- Docker Compose
- GitHub Actions

## Documentation map

1. `docs/01_PRD.md`
2. `docs/02_PIPELINE_FLOW.md`
3. `docs/03_SYSTEM_ARCHITECTURE.md`
4. `docs/04_AGENT_SPECIFICATIONS.md`
5. `docs/05_MCP_SERVER_SPEC.md`
6. `docs/06_DATA_CONTRACTS.md`
7. `docs/07_MARKET_DATA_PROVIDER_SPEC.md`
8. `docs/08_SIGNAL_ANALYTICS_SPEC.md`
9. `docs/09_POINT_IN_TIME_AND_LEAKAGE.md`
10. `docs/10_OBSERVABILITY_AND_SECURITY.md`
11. `docs/11_TEST_STRATEGY.md`
12. `docs/12_DEVOPS_AND_DEPLOYMENT.md`
13. `docs/13_IMPLEMENTATION_ROADMAP.md`
14. `docs/14_ACCEPTANCE_CRITERIA.md`
15. `docs/15_PORTFOLIO_DEMO.md`
16. `docs/16_ARCHITECTURE_DECISIONS.md`
17. `docs/17_REPORT_TEMPLATE.md`
18. `docs/18_RUNBOOK.md`

Implementation control:
- `ANTIGRAVITY_HANDOFF.md`
- `CLAUDE.md`
- `.claude/agents/*`

## Current external references

MCP:
- https://blog.modelcontextprotocol.io/posts/2026-07-28/
- https://py.sdk.modelcontextprotocol.io/protocol-versions/

Market/news providers:
- https://www.alphavantage.co/documentation/
- https://polygon.io/docs/rest/stocks/news
- https://polygon.io/docs/rest/stocks/snapshots/single-ticker-snapshot

Experiment/model lifecycle:
- https://mlflow.org/docs/latest/model-registry/

Observability:
- https://opentelemetry.io/docs/languages/python/
