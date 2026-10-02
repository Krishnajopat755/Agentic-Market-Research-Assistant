# Pipeline Flow

## 1. End-to-end flow

```mermaid
flowchart TD
    A[Watchlist + Analysis Timestamp] --> B[Orchestrator]
    B --> C[Validate Request]
    C --> D[Market Data Agent]
    D --> E[MCP: fetch_market_snapshot]
    D --> F[MCP: fetch_historical_bars]
    D --> G[MCP: fetch_market_benchmark]
    D --> H[MCP: fetch_market_news]
    E --> I[Persist Raw Observations]
    F --> I
    G --> I
    H --> J[Sentiment & Technical Agent]
    I --> J
    J --> K[MCP: normalize_and_deduplicate_news]
    J --> L[MCP: compute_sentiment]
    J --> M[MCP: compute_technical_indicators]
    J --> N[MCP: build_research_features]
    K --> O[Analytics Quality Gate]
    L --> O
    M --> O
    N --> O
    O --> P[MCP: run_signal_model]
    P --> Q[Synthesis & Report Agent]
    Q --> R[MCP: get_research_evidence]
    Q --> S[MCP: validate_report_claims]
    Q --> T[MCP: render_daily_report]
    T --> U[Completed Research Run]
```

## 2. Historical point-in-time flow

```mermaid
flowchart LR
    A[Cutoff T] --> B[Retrieve data <= T]
    B --> C[Normalize timestamps]
    C --> D[Create features at T]
    D --> E[Predict t+h]
    E --> F[Construct future label only for evaluation]
    D --> G[Model]
    F --> H[Walk-forward evaluation]
```

The feature row at T must never consume observations with information time > T.

## 3. State machine

```mermaid
stateDiagram-v2
    [*] --> REQUEST_VALIDATED
    REQUEST_VALIDATED --> MARKET_DATA_COLLECTED
    MARKET_DATA_COLLECTED --> NEWS_COLLECTED
    NEWS_COLLECTED --> DATA_NORMALIZED
    DATA_NORMALIZED --> ANALYTICS_COMPLETE
    ANALYTICS_COMPLETE --> SIGNAL_GENERATED
    SIGNAL_GENERATED --> EVIDENCE_BOUND
    EVIDENCE_BOUND --> REPORT_GENERATED
    REPORT_GENERATED --> COMPLETED
    REQUEST_VALIDATED --> FAILED
    MARKET_DATA_COLLECTED --> FAILED
    NEWS_COLLECTED --> FAILED
    DATA_NORMALIZED --> FAILED
    ANALYTICS_COMPLETE --> FAILED
    SIGNAL_GENERATED --> FAILED
    EVIDENCE_BOUND --> FAILED
    REPORT_GENERATED --> FAILED
    FAILED --> REQUEST_VALIDATED: resume/retry
```

## 4. Fan-out/fan-in

For a watchlist:
1. validate all symbols;
2. fan out data collection under a bounded concurrency limit;
3. normalize independently;
4. fan in into a single run state;
5. analyze each symbol;
6. produce per-symbol sections plus market-level synthesis.

A provider error for one symbol must not silently invalidate other successful symbols unless the missing symbol is essential to the configured research objective.

## 5. Failure handling

Errors:
- `TRANSIENT_PROVIDER_ERROR` -> bounded retry;
- `RATE_LIMITED` -> backoff;
- `AUTH_ERROR` -> fail fast;
- `STALE_DATA` -> warn or block per policy;
- `EMPTY_RESULT` -> required/optional source policy;
- `SCHEMA_CHANGED` -> fail fast and record provider incident.

## 6. Daily operation

A scheduled run should:
1. determine the intended analysis timestamp;
2. determine market session state;
3. fetch data through the cutoff;
4. analyze news and indicators;
5. generate signal;
6. bind evidence;
7. render report;
8. archive immutable artifacts.
