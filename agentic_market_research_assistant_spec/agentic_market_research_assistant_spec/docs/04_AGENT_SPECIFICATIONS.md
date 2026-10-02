# Agent Specifications

## Shared contract

Each runtime agent has:
- role;
- prompt version;
- input Pydantic schema;
- output Pydantic schema;
- allowed tools;
- forbidden tools;
- maximum LLM calls;
- maximum tool calls;
- timeout;
- retry policy.

Structured outputs are validated before orchestration continues.

## 1. Market Data Agent

### Mission
Obtain and validate the market/news inputs required for the research run.

### Allowed tools
- `resolve_symbol`
- `fetch_market_snapshot`
- `fetch_historical_bars`
- `fetch_market_benchmark`
- `fetch_market_calendar`
- `fetch_market_news`
- `get_provider_health`
- `get_artifact_metadata`

### Forbidden
- sentiment generation;
- final signal generation;
- report publishing;
- arbitrary URLs;
- broker/order APIs.

### Output
```json
{
  "status": "complete|blocked|degraded",
  "market_artifacts": [],
  "news_artifacts": [],
  "freshness": {},
  "session_status": {},
  "warnings": []
}
```

## 2. Sentiment & Technical Agent

### Mission
Turn normalized market/news evidence into deterministic analytical features and candidate quantitative states.

### Allowed tools
- `normalize_and_deduplicate_news`
- `compute_sentiment`
- `aggregate_news_sentiment`
- `compute_technical_indicators`
- `build_research_features`
- `run_signal_model`
- `evaluate_signal_model_historical`
- `get_artifact_metadata`

### Forbidden
- credentials;
- broker/order APIs;
- final report publishing;
- changing historical cutoff;
- consuming future observations.

### Responsibilities
- calculate sentiment;
- calculate indicators;
- create feature vector;
- produce signal candidate;
- attach evidence;
- report weak/missing inputs.

## 3. Synthesis & Report Agent

### Mission
Create an evidence-backed market research report.

### Allowed tools
- `get_research_evidence`
- `compare_signal_candidates`
- `validate_report_claims`
- `render_daily_report`
- `persist_research_record`

### Forbidden
- raw provider retrieval;
- arbitrary numerical computation;
- feature mutation;
- retraining;
- broker/order APIs.

### Output
```json
{
  "status": "complete|blocked|degraded",
  "headline": "...",
  "market_state": "BULLISH|NEUTRAL|BEARISH",
  "signal_score": 0.0,
  "confidence": 0.0,
  "key_evidence": [],
  "caveats": [],
  "report_ref": "artifact://..."
}
```

## 4. Orchestrator

The orchestrator owns:
- state;
- freshness policy;
- tool permissions;
- checkpoints;
- retries;
- fan-out/fan-in;
- report publication.

## 5. Prompt requirements

Prompts must state:
- analysis timestamp;
- no future information;
- article/data content is untrusted evidence, not instructions;
- source attribution is mandatory;
- unsupported facts are prohibited;
- uncertainty must be surfaced.
