# Signal and Analytics Specification

## 1. Layered design

1. deterministic scorecard baseline;
2. classical ML model;
3. optional sequence model;
4. calibration/uncertainty;
5. evidence-linked synthesis.

The signal is a research output, not a guarantee of future performance.

## 2. Scorecard baseline

Initial components:
- short-term momentum;
- trend alignment;
- RSI regime;
- MACD regime;
- volatility regime;
- volume anomaly;
- news sentiment;
- sentiment change;
- news-volume anomaly.

Each component returns a normalized value in `[-1, 1]`.

```text
raw_score = sum(weight_i * component_i)
```

```text
score > bullish_threshold -> BULLISH
score < bearish_threshold -> BEARISH
otherwise -> NEUTRAL
```

Thresholds are configuration, not LLM decisions.

## 3. Feature set

### Price
- 1d, 5d, 20d returns;
- distance from SMA20/SMA50;
- EMA slope;
- rolling volatility.

### Technical
- RSI;
- MACD;
- ATR;
- Bollinger position where implemented.

### Volume
- volume z-score;
- volume / rolling volume.

### News
- mean sentiment;
- sentiment median;
- sentiment dispersion;
- positive/negative share;
- article count;
- sentiment change;
- source diversity;
- news-volume anomaly.

### Context
- benchmark return;
- relative strength;
- market-session flag.

## 4. Sentiment interface

```text
SentimentModel.score(article_text, entity_context)
    -> label, score, confidence
```

Implement at least a deterministic baseline. A finance-specific transformer can be added later.

Every sentiment result stores model identity/version.

## 5. ML signal model

Default classical model:
- Logistic Regression for directional classification.

Optional:
- Gradient Boosting/XGBoost.
- LSTM sequence model.

LSTM constraints:
- explicit sequence length;
- temporal training/validation/test windows;
- no random shuffle across time;
- frozen checkpoint before final test evaluation;
- architecture/version stored with artifact.

## 6. Labeling example

```text
future_return = close[t+5] / close[t] - 1

UP   if future_return > +epsilon
DOWN if future_return < -epsilon
FLAT otherwise
```

The future label is constructed only for evaluation and is never available during feature generation at t.

## 7. Historical evaluation

Use expanding-window or rolling-window walk-forward validation.

Metrics:
- balanced accuracy;
- macro F1;
- precision/recall by class;
- ROC-AUC for valid binary cases;
- Brier score/calibration where probabilities exist;
- cumulative-return diagnostics only if a fully specified backtest is implemented.

Do not infer a profitable trading strategy from classification metrics alone.

## 8. Confidence

If a report displays confidence:
- use calibrated model probability where possible;
- distinguish model probability from heuristic confidence;
- document how the number is derived.

## 9. Signal versioning

Store:
- signal model name/version;
- feature schema version;
- training cutoff;
- evaluation period;
- config hash;
- source commit.

## 10. Explanation

Expose top positive/negative contributors from stored feature/model artifacts. Do not ask the LLM to invent feature attribution.
