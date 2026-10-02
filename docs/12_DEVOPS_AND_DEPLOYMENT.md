# DevOps and Deployment

## 1. Local stack

```text
api
orchestrator
finance-mcp
postgres
minio
mlflow
otel-collector (optional)
```

## 2. Commands

```bash
make install
make lint
make typecheck
make test
make test-e2e
make up
make down
make mcp-dev
make demo-aapl
make demo-watchlist
```

## 3. Environment

```text
ANTHROPIC_API_KEY=
ALPHAVANTAGE_API_KEY=
POLYGON_API_KEY=
DATABASE_URL=
MLFLOW_TRACKING_URI=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
MLFLOW_S3_ENDPOINT_URL=
ARTIFACT_BUCKET=
OTEL_EXPORTER_OTLP_ENDPOINT=
LOG_LEVEL=INFO
```

Never commit real credentials.

## 4. Fixture vs live mode

### Fixture mode
- no external API key;
- deterministic;
- CI-safe;
- archived/synthetic responses.

### Live mode
- credentials required;
- source and entitlement visible;
- quotas/rate limits respected;
- live data excluded from reproducibility tests.

## 5. CI/CD

PR: lint, types, unit, contract, point-in-time tests.

Main: integration, E2E, Docker builds.

Release: version, changelog, lockfile review, migration, demo verification.

## 6. Health

API:
- `/health/live`
- `/health/ready`

Readiness checks Postgres, artifact store, and MLflow. Provider availability is a diagnostic, not a hard liveness dependency.

## 7. Scheduling

v1: CLI + optional Cron/GitHub Actions.

Production-like: scheduler creates a run request with an explicit analysis timestamp. Analytics code never silently uses local `now`.
