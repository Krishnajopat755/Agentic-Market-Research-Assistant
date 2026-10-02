# Architecture Decision Records

## ADR-001 — Provider abstraction

Use provider interfaces and adapters so domain logic is independent of vendor quotas, schema, entitlements, and exchanges.

## ADR-002 — Alpha Vantage initial adapter

Use Alpha Vantage first because its current documentation exposes daily equity time series, news/sentiment, and technical-indicator APIs appropriate to the MVP. Provider plan/entitlement remains runtime configuration.

Reference: https://www.alphavantage.co/documentation/

## ADR-003 — Polygon/Massive secondary adapter

Add a second provider adapter after MVP to demonstrate portability and richer provider integration where supported.

Reference: https://polygon.io/docs/rest/stocks/news

## ADR-004 — Three runtime agents

Three specialists are sufficient: acquisition, analysis, synthesis. More agents should be added only when responsibilities are genuinely separable.

## ADR-005 — MCP execution boundary

All external retrieval and deterministic analytics use MCP tools. This demonstrates agentic tool-calling while preserving testable execution boundaries.

## ADR-006 — No trading execution

No brokerage/order integration in v1. The project stays a research/agentic engineering artifact.

## ADR-007 — Point-in-time schema

Every observation stores event/publication, retrieval, availability, and cutoff metadata. Finance research depends on what was knowable then.

## ADR-008 — Walk-forward evaluation

No random time-series split for directional signal models.

## ADR-009 — LSTM extension

Add LSTM only after the scorecard, classical model, and leakage suite are correct.

## ADR-010 — MLflow

Use MLflow for run/model lineage and versioned model artifacts.

Reference: https://mlflow.org/docs/latest/model-registry/

## ADR-011 — OpenTelemetry

Use vendor-neutral traces and metrics for agent/tool/provider execution.

Reference: https://opentelemetry.io/docs/languages/python/

## ADR-012 — Current MCP baseline

Target MCP 2026-07-28 and official Python SDK v2.

References:
- https://blog.modelcontextprotocol.io/posts/2026-07-28/
- https://py.sdk.modelcontextprotocol.io/protocol-versions/
