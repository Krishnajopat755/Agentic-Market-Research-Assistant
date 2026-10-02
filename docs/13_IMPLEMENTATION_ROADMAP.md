# Implementation Roadmap

## Phase 0 — Bootstrap
- repo;
- uv;
- Pydantic contracts;
- config;
- tests;
- CI.

Exit: clean project builds.

## Phase 1 — Finance core
Implement:
1. normalized market schema;
2. provider adapter interface;
3. Alpha Vantage fixture adapter;
4. news normalization/dedup;
5. indicators;
6. sentiment interface;
7. scorecard signal;
8. report data model.

Exit: one function generates an AAPL report from fixtures.

## Phase 2 — Point-in-time ML
Implement:
- historical dataset builder;
- walk-forward split;
- labels;
- look-ahead test;
- baseline classifier;
- evaluation metrics.

Exit: historical signal model passes leakage suite.

## Phase 3 — Storage/lineage
Implement artifacts, Postgres metadata, MLflow, model versioning, source/config/code hashes.

Exit: complete non-agentic run is traceable.

## Phase 4 — MCP
Expose finance core as typed MCP tools with role/state restrictions, idempotency, stdio, and Streamable HTTP.

Exit: MCP contracts green.

## Phase 5 — Orchestrator
Implement state graph, checkpointing, retries, fan-out/fan-in, and degrade/approval policy.

Exit: scripted fake-agent run works.

## Phase 6 — Runtime agents
Implement:
1. Market Data Agent;
2. Sentiment & Technical Agent;
3. Synthesis & Report Agent.

Each gets its own prompt, output schema, tool allowlist, and tests.

## Phase 7 — Security/observability
Add OpenTelemetry, structured logs, provider health, rate-limit handling, prompt-injection tests, secret redaction, and permission tests.

## Phase 8 — UX/demo
Add CLI, FastAPI, report renderer, MCP Inspector demo, MLflow screenshots, trace screenshots.

## Phase 9 — Finance ML extension
Optional:
- finance transformer sentiment;
- LSTM;
- calibrated probabilities;
- benchmark-relative/regime features.

Do not start here.
