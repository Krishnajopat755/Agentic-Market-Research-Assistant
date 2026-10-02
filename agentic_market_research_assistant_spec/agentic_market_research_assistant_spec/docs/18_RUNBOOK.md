# Operational Runbook

## Provider unavailable

1. Detect error.
2. Retry only retryable failures.
3. Respect Retry-After/backoff.
4. Use configured secondary provider only when policy allows.
5. Mark source degraded.
6. Continue only if minimum evidence requirements remain satisfied.

## Stale data

If data age exceeds configured thresholds:
- never present it as current;
- add a warning;
- optionally block signal generation.

Example configuration:
```text
MAX_MARKET_STALENESS_SECONDS=1800
MAX_NEWS_STALENESS_SECONDS=7200
```

These are engineering examples, not universal finance rules.

## Excessive news volume

Cap processing, retain truncation metadata, and do not imply all articles were analyzed.

## Duplicate news

Use provider ID/URL first; then title + publisher + time similarity. Preserve the duplicate group.

## Weak model

If validation performance is below baseline:
- do not hide it;
- generate `NO_SIGNAL` or `LOW_CONFIDENCE` where configured;
- start a new research run for hypothesis changes rather than tuning against final test evidence.

## Rate limit

Do not retry authorization failures. Retry documented transient/rate-limit failures with bounded backoff and caching.

## Rollback

Model rollback uses an immutable prior MLflow model version. Prompt rollback pins an older prompt version and creates a new run ID.

## Incident evidence

Collect run ID, provider, request ID, trace ID, tool, timestamp, error code, and artifact references.
