# Product Requirements Document
## Agentic Market Research Assistant

**Status:** Build specification  
**Target:** Portfolio-quality v1  
**Primary use:** Daily market research workflow for selected public-market instruments  
**Primary portfolio signal:** Agent orchestration + tool-calling + MCP + finance ML/NLP

## 1. Problem

Market research requires disconnected workflows: current market data, recent news, sentiment, technical indicators, historical context, and report synthesis. A notebook can produce numbers but does not itself demonstrate specialized agents, tool boundaries, reliability, provenance, or point-in-time correctness.

This project demonstrates those engineering concerns in one finance-domain system.

## 2. Goal

Given a watchlist and a research timestamp, generate an evidence-linked daily report containing:
- market snapshot;
- fresh news;
- deduplicated article set;
- article-level sentiment;
- aggregate sentiment;
- technical indicators;
- quantitative features;
- a bounded research signal/state;
- confidence/quality metadata;
- scenario analysis;
- cited evidence;
- known data limitations.

A complete run must be reproducible from archived inputs where licensing permits.

## 3. Non-goals

v1 must not:
- place orders;
- connect to a live broker;
- execute real-money trading;
- provide individualized investment advice;
- claim certainty about future price direction;
- scrape sites that prohibit automated access;
- bypass provider authentication or rate limits;
- use undisclosed news sources;
- train on future observations when evaluating historical signals.

## 4. Supported instruments

v1:
- US equities/ETFs with provider-supported symbols.

Architecture may later support:
- Indian equities;
- FX;
- crypto;
- indices.

## 5. User input

Required:
- watchlist symbols;
- analysis timestamp/time zone.

Optional:
- lookback window;
- news window;
- preferred provider;
- market/session;
- research horizon;
- indicator configuration;
- signal thresholds;
- model version.

Example:

```yaml
symbols:
  - AAPL
  - MSFT
  - NVDA
analysis_timestamp: "2026-09-25T16:10:00-04:00"
timezone: "America/New_York"
market: "US"
price_lookback_days: 120
news_lookback_hours: 24
sentiment_model: "finance_sentiment_default"
signal_horizon_bars: 5
```

## 6. Functional requirements

### FR-01 Watchlist validation
Validate symbols, market, time zone, and analysis timestamp.

### FR-02 Market retrieval
Retrieve latest available quote/snapshot where permitted and historical OHLCV with provider timestamp/entitlement metadata.

### FR-03 News retrieval
Retrieve recent/historical articles with source, article ID, title, publication timestamp, URL, tickers/entities, and description/summary when licensed.

### FR-04 News normalization
Normalize timestamps to UTC internally, canonical ticker identifiers, source names, URLs, and sentiment scale.

### FR-05 News deduplication
Detect duplicates using provider IDs, canonical URLs, normalized title hashes, and publisher/time similarity. Preserve why records were merged.

### FR-06 Data freshness
Every observation carries `event_time`, `retrieved_at`, `as_of`, and `freshness_seconds`. Reports must distinguish stale from fresh data.

### FR-07 Sentiment analysis
Produce article-level label, scalar score, and model identity. Confidence is optional and must be methodologically defined.

### FR-08 Technical analysis
At minimum: SMA, EMA, RSI, MACD, ATR/volatility proxy, volume trend, and returns.

### FR-09 Research features
Combine price momentum, trend, volatility, volume, sentiment level/change, news volume, abnormal-news-volume proxy, and benchmark context where available.

### FR-10 Research signal
Generate a quantitative state using either a deterministic scorecard or versioned ML model.

Output example:
```json
{
  "state": "BULLISH|NEUTRAL|BEARISH",
  "score": 0.23,
  "confidence": 0.64,
  "horizon_bars": 5
}
```

### FR-11 Evidence binding
Every material signal component references its evidence artifact/article/model.

### FR-12 Historical evaluation
Use point-in-time walk-forward/expanding-window evaluation. No shuffled random split for time-series prediction.

### FR-13 Report
Generate Markdown, HTML, JSON, and charts.

### FR-14 Daily run
Support CLI, API, and optional scheduler.

### FR-15 Run persistence
Persist inputs, observations, transformations, agent decisions, tool calls, model version, report, and lineage.

## 7. Agentic requirements

### AR-01 Specialization
At least three runtime agents:
1. Market Data Agent.
2. Sentiment & Technical Agent.
3. Synthesis & Report Agent.

### AR-02 Orchestrator
A dedicated orchestrator controls state and permissions.

### AR-03 MCP tools
All external data retrieval and deterministic analytics happen through MCP tools.

### AR-04 Least privilege
Agents only see tools required for their responsibility.

### AR-05 Structured outputs
Agent decisions are Pydantic-validated.

### AR-06 Evidence first
The synthesis agent cannot make a material factual claim without an evidence reference.

### AR-07 No hidden execution
No arbitrary shell/Python/browser-execution tool is exposed to runtime agents.

## 8. Non-functional requirements

### NFR-01 Point-in-time correctness
Historical research must reproduce what was knowable at the requested timestamp, subject to documented provider limitations.

### NFR-02 Reproducibility
Persist source references, provider, retrieval time, config, model version, code commit, random seed, feature schema, and prompt version.

### NFR-03 Freshness
Report data age and stale-source warnings.

### NFR-04 Reliability
Retry transient provider failures with bounded backoff. Surface permanent failures.

### NFR-05 Rate-limit safety
Use quotas, Retry-After, exponential backoff, and caching where permitted.

### NFR-06 Security
API keys never enter prompts or logs.

### NFR-07 Auditability
Every report section maps back to data/evidence/artifacts.

### NFR-08 Portability
Local demo runs via Docker Compose without requiring paid live-data access.

## 9. Success metrics

Engineering:
- >=80% deterministic-core test coverage;
- 100% MCP critical tools contract-tested;
- zero arbitrary execution tools;
- 100% material report claims traceable to evidence;
- successful failure/retry demonstration;
- successful stale-data demonstration;
- successful look-ahead-bias test.

Finance/ML:
- baseline scorecard;
- ML candidate comparison;
- walk-forward evaluation;
- calibration/uncertainty where implemented.

Portfolio:
- three runtime agents are visibly distinct;
- MCP tool trace can be demonstrated;
- report shows market/news/technical evidence;
- MLflow contains model/evaluation lineage;
- OpenTelemetry traces connect agent -> MCP -> analytics.

## 10. Release definition

v1 is complete when:
- AAPL and MSFT demos can run using configurable provider or archived fixtures;
- a full report is produced;
- one market-data failure recovery is demonstrated;
- stale-news detection is demonstrated;
- a synthetic look-ahead-bias test passes;
- the synthesis agent cannot call raw provider tools directly.
