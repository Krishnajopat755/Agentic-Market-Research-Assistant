# Data Contracts

## 1. AnalysisRequest

```json
{
  "run_id": "uuid",
  "symbols": ["AAPL", "MSFT"],
  "analysis_timestamp": "2026-09-25T16:10:00-04:00",
  "timezone": "America/New_York",
  "market": "US",
  "price_lookback_days": 120,
  "news_lookback_hours": 24,
  "signal_horizon_bars": 5
}
```

## 2. MarketObservation

```json
{
  "symbol": "AAPL",
  "event_time": "...",
  "retrieved_at": "...",
  "as_of": "...",
  "open": 0,
  "high": 0,
  "low": 0,
  "close": 0,
  "volume": 0,
  "source": "alphavantage",
  "provider_record_id": "...",
  "entitlement": "delayed",
  "artifact_ref": "artifact://..."
}
```

## 3. NewsArticle

```json
{
  "article_id": "stable-hash",
  "provider_article_id": "...",
  "publisher": "...",
  "title": "...",
  "description": "...",
  "article_url": "...",
  "published_at": "...",
  "retrieved_at": "...",
  "tickers": ["AAPL"],
  "source_provider": "...",
  "duplicate_group_id": null,
  "sentiment": {
    "label": "positive|neutral|negative",
    "score": 0.0,
    "model": "..."
  }
}
```

## 4. TechnicalSnapshot

```json
{
  "symbol": "AAPL",
  "as_of": "...",
  "sma_20": 0,
  "sma_50": 0,
  "ema_20": 0,
  "rsi_14": 0,
  "macd": 0,
  "macd_signal": 0,
  "atr_14": 0,
  "realized_volatility_20": 0,
  "volume_zscore_20": 0
}
```

## 5. SignalResult

```json
{
  "symbol": "AAPL",
  "as_of": "...",
  "horizon_bars": 5,
  "method": "scorecard|ml",
  "model_version": "signal-model-1.0.0",
  "state": "BULLISH|NEUTRAL|BEARISH",
  "score": 0.0,
  "confidence": 0.0,
  "feature_artifact_ref": "artifact://...",
  "evidence_refs": [],
  "limitations": []
}
```

## 6. ResearchEvidence

```json
{
  "claim_id": "claim-123",
  "claim_text": "...",
  "evidence_type": "market|news|indicator|model",
  "evidence_ref": "artifact://...",
  "source_url": "...",
  "source_timestamp": "...",
  "calculation_ref": null
}
```

## 7. Artifact kinds

```text
raw_market
normalized_market
raw_news
normalized_news
sentiment
technical_indicators
research_features
signal
historical_evaluation
report
model
model_card
```

Artifacts are immutable and content-addressed where practical.
