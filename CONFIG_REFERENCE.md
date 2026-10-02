# Configuration Reference

Example:

```yaml
project:
  name: agentic-market-research-assistant
  mode: fixture

research:
  timezone: America/New_York
  news_lookback_hours: 24
  price_lookback_days: 120
  signal_horizon_bars: 5
  stale_market_seconds: 1800
  stale_news_seconds: 7200

providers:
  market_primary: alphavantage
  market_secondary: polygon
  allow_live: false
  max_concurrency: 2

sentiment:
  provider: local_finance_baseline
  max_article_chars: 12000

signal:
  method: scorecard
  bullish_threshold: 0.20
  bearish_threshold: -0.20
  min_evidence_count: 3

runtime:
  max_llm_calls_per_agent: 4
  max_tool_calls_per_agent: 20
  max_retries: 3

security:
  allow_broker_tools: false
  allow_arbitrary_url_fetch: false
```

Thresholds are engineering defaults for the portfolio project, not universal finance rules.
