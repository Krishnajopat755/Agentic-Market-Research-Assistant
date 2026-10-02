"""Deterministic scorecard signal generator matching Section 2 of Signal Analytics Spec."""

from src.contracts.features import ResearchFeatures
from src.contracts.signal import SignalContributor, SignalResult
from src.finance_core.market_data.normalization import normalize_datetime

DEFAULT_WEIGHTS = {
    "momentum": 0.15,
    "trend": 0.15,
    "rsi": 0.10,
    "macd": 0.10,
    "sentiment": 0.25,
    "sentiment_change": 0.10,
    "volume": 0.10,
    "volatility": 0.05,
}


def clamp(val: float, min_val: float = -1.0, max_val: float = 1.0) -> float:
    return max(min_val, min(max_val, val))


def compute_scorecard_signal(
    features: ResearchFeatures,
    bullish_threshold: float = 0.20,
    bearish_threshold: float = -0.20,
    weights: dict[str, float] | None = None,
    horizon_bars: int = 5,
    model_version: str = "scorecard-v1.0.0",
) -> SignalResult:
    """
    Compute deterministic scorecard signal.
    Every component returns a normalized value in [-1, 1].
    raw_score = sum(weight_i * component_i)
    """
    f = features.features
    w = weights or DEFAULT_WEIGHTS

    # Component 1: Momentum (5d return scaled, +/-5% maps to +/-1.0)
    ret_5d = f.get("return_5d", 0.0)
    comp_momentum = clamp(ret_5d / 0.05)

    # Component 2: Trend alignment (distance from SMA50, +/-10% maps to +/-1.0)
    dist_sma50 = f.get("dist_sma_50", 0.0)
    comp_trend = clamp(dist_sma50 / 0.10)

    # Component 3: RSI regime (centered normalized RSI in [-1, 1])
    comp_rsi = clamp(f.get("rsi_norm", 0.0))

    # Component 4: MACD regime (MACD histogram normalized, +/-1% of price maps to +/-1.0)
    macd_hist = f.get("macd_hist_norm", 0.0)
    comp_macd = clamp(macd_hist / 0.01)

    # Component 5: News sentiment (mean sentiment in [-1, 1])
    comp_sentiment = clamp(f.get("news_mean_sentiment", 0.0))

    # Component 6: Sentiment change (+/-0.5 change maps to +/-1.0)
    sent_change = f.get("news_sentiment_change", 0.0)
    comp_sent_change = clamp(sent_change / 0.50)

    # Component 7: Volume anomaly (z-score: high positive z-score amplifies momentum direction)
    vol_zscore = f.get("volume_zscore", 0.0)
    vol_scaled = clamp(vol_zscore / 2.0, 0.0, 1.0)
    comp_volume = vol_scaled * comp_momentum  # volume confirms price direction

    # Component 8: Volatility regime (high volatility reduces bullishness, penalizes score)
    vol_20d = f.get("volatility_20d", 0.20)
    comp_volatility = clamp(1.0 - (vol_20d / 0.35))  # lower vol is positive for trend continuation

    components = {
        "momentum": comp_momentum,
        "trend": comp_trend,
        "rsi": comp_rsi,
        "macd": comp_macd,
        "sentiment": comp_sentiment,
        "sentiment_change": comp_sent_change,
        "volume": comp_volume,
        "volatility": comp_volatility,
    }

    contributors: list[SignalContributor] = []
    total_score = 0.0
    weight_sum = 0.0

    for name, weight in w.items():
        val = components.get(name, 0.0)
        contrib = weight * val
        total_score += contrib
        weight_sum += weight

        if contrib > 0.02:
            direction = "BULLISH"
        elif contrib < -0.02:
            direction = "BEARISH"
        else:
            direction = "NEUTRAL"

        contributors.append(
            SignalContributor(
                name=name,
                weight=round(weight, 3),
                value=round(val, 4),
                contribution=round(contrib, 4),
                direction=direction,
            )
        )

    # Normalize score
    normalized_score = total_score / weight_sum if weight_sum > 0 else 0.0
    normalized_score = clamp(round(normalized_score, 4))

    # Determine State
    if normalized_score >= bullish_threshold:
        state = "BULLISH"
    elif normalized_score <= bearish_threshold:
        state = "BEARISH"
    else:
        state = "NEUTRAL"

    # Sort contributors by absolute contribution descending
    contributors.sort(key=lambda c: abs(c.contribution), reverse=True)

    # Confidence calculation: based on consistency of contributors and magnitude
    concordant = sum(
        1
        for c in contributors
        if (c.contribution > 0 if normalized_score > 0 else c.contribution < 0)
    )
    concordance_ratio = concordant / len(contributors) if contributors else 0.5
    confidence = clamp(0.40 + 0.35 * abs(normalized_score) + 0.25 * concordance_ratio, 0.0, 1.0)

    # Limitations & Warnings
    limitations: list[str] = [
        "Scorecard is a bounded heuristic model and does not account for regime shifts or macroeconomic shocks.",
        "Model outputs are research candidates, not trade signals or fiduciary investment advice.",
    ]
    if f.get("news_article_count", 0) < 3:
        limitations.append(
            f"Low news volume ({int(f.get('news_article_count', 0))} articles) reduces sentiment statistical significance."
        )
    if vol_20d > 0.40:
        limitations.append(
            f"Elevated realized volatility ({vol_20d:.1%}) increases signal uncertainty."
        )

    evidence_refs: list[str] = [
        f"technical_indicators:{features.symbol}",
        f"aggregate_sentiment:{features.symbol}",
        f"features:{features.symbol}:{features.feature_schema_version}",
    ]

    return SignalResult(
        symbol=features.symbol,
        as_of=normalize_datetime(features.as_of),
        horizon_bars=horizon_bars,
        method="scorecard",
        model_version=model_version,
        state=state,
        score=normalized_score,
        confidence=round(confidence, 4),
        feature_artifact_ref=features.artifact_ref,
        top_contributors=contributors[:5],
        evidence_refs=evidence_refs,
        limitations=limitations,
    )
