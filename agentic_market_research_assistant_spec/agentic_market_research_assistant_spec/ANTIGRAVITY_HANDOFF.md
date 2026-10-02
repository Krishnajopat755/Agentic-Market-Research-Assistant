# Antigravity Handoff

## Mission

Build the Agentic Market Research Assistant described in the documentation.

This is **not** a news summarizer and **not** a simple three-prompt chatbot.

The project must visibly demonstrate:
1. multi-agent orchestration;
2. finance API tool-calling;
3. MCP;
4. deterministic sentiment + technical analytics;
5. point-in-time correctness;
6. time-series ML evaluation;
7. evidence-linked reporting;
8. observability;
9. provider-failure recovery;
10. secure tool boundaries.

## Read first

Read:
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
15. `docs/16_ARCHITECTURE_DECISIONS.md`
16. `CLAUDE.md`

## Non-negotiable implementation rules

### Rule 1 — Core before agents
First build the finance core with fixture data.

### Rule 2 — Point-in-time correctness is a release blocker
Future-data tests must pass before full runtime-agent implementation.

### Rule 3 — MCP is narrow
No arbitrary Python, shell, browser, SQL, URL fetch, or filesystem tools.

### Rule 4 — Provider abstraction
Do not put Alpha Vantage/Polygon JSON shapes into domain code.

### Rule 5 — Evidence binding
Every material report claim must trace to structured evidence.

### Rule 6 — No execution
Do not add broker/order APIs.

### Rule 7 — Live APIs are optional for CI
Fixture mode must fully work without provider credentials.

### Rule 8 — LSTM later
Do not make LSTM the first implementation.

## Phase order

A. Bootstrap  
B. Finance core + fixture provider  
C. Point-in-time historical evaluation  
D. Storage/MLflow  
E. MCP server  
F. Orchestrator  
G. Runtime agents  
H. Security/observability  
I. Live provider adapters  
J. Demo polish  
K. LSTM extension

## Required demo

```bash
make demo-aapl
```

Must generate market snapshot, news set, sentiment, indicators, research features, signal, HTML/Markdown/JSON report, and lineage metadata.

## Preferred dependencies

```text
python >=3.11
pydantic
pydantic-settings
pandas
numpy
scikit-learn
optuna
langgraph
anthropic
mcp
mlflow
sqlalchemy
alembic
psycopg
boto3
fastapi
uvicorn
opentelemetry-api
opentelemetry-sdk
structlog
httpx
pytest
pytest-asyncio
pytest-cov
mypy
ruff
```

Optional: torch, transformers, xgboost.

## Definition of done

Every checkbox in `docs/14_ACCEPTANCE_CRITERIA.md` must be implemented/tested or explicitly deferred with a reason.
