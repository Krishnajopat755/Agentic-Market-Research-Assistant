"""Research feature vector builder strictly point-in-time."""

from collections.abc import Sequence
from datetime import datetime

from src.contracts.features import ResearchFeatures
from src.contracts.market import MarketObservation
from src.contracts.news import AggregateSentiment
from src.contracts.technical import TechnicalSnapshot
from src.finance_core.market_data.normalization import normalize_datetime


def build_research_features(
    symbol: str,
    as_of: datetime,
    technical: TechnicalSnapshot,
    sentiment: AggregateSentiment,
    benchmark_observations: Sequence[MarketObservation] | None = None,
) -> ResearchFeatures:
    """
    Combine technical indicators, sentiment aggregate, and benchmark context
    into a standardized feature vector for downstream scorecard and ML models.
    """
    price = technical.price
    feats: dict[str, float] = {}

    # 1. Price Momentum & Returns
    feats["return_1d"] = technical.returns_1d if technical.returns_1d is not None else 0.0
    feats["return_5d"] = technical.returns_5d if technical.returns_5d is not None else 0.0
    feats["return_20d"] = technical.returns_20d if technical.returns_20d is not None else 0.0

    # 2. Moving Average Distances
    feats["dist_sma_20"] = (
        (price - technical.sma_20) / technical.sma_20 if technical.sma_20 else 0.0
    )
    feats["dist_sma_50"] = (
        (price - technical.sma_50) / technical.sma_50 if technical.sma_50 else 0.0
    )

    # 3. Technical Oscillators & Trend
    # Center RSI in [-1, 1] range: 50 -> 0, 70 -> 0.4, 30 -> -0.4
    if technical.rsi_14 is not None:
        feats["rsi_norm"] = (technical.rsi_14 - 50.0) / 50.0
    else:
        feats["rsi_norm"] = 0.0

    # Normalized MACD
    if technical.macd is not None and price > 0:
        feats["macd_norm"] = technical.macd / price
        feats["macd_hist_norm"] = (
            (technical.macd_hist / price) if technical.macd_hist is not None else 0.0
        )
    else:
        feats["macd_norm"] = 0.0
        feats["macd_hist_norm"] = 0.0

    # Volatility / ATR
    if technical.atr_14 is not None and price > 0:
        feats["atr_norm"] = technical.atr_14 / price
    else:
        feats["atr_norm"] = 0.0

    feats["volatility_20d"] = (
        technical.realized_volatility_20 if technical.realized_volatility_20 is not None else 0.0
    )

    # 4. Volume Anomaly
    feats["volume_zscore"] = (
        technical.volume_zscore_20 if technical.volume_zscore_20 is not None else 0.0
    )

    # 5. News Sentiment Features
    feats["news_mean_sentiment"] = sentiment.mean_score
    feats["news_median_sentiment"] = sentiment.median_score
    feats["news_sentiment_dispersion"] = sentiment.sentiment_dispersion
    feats["news_sentiment_change"] = sentiment.sentiment_change
    feats["news_positive_share"] = sentiment.positive_share
    feats["news_negative_share"] = sentiment.negative_share
    feats["news_article_count"] = float(sentiment.article_count)
    feats["news_source_diversity"] = float(sentiment.source_diversity)
    feats["news_abnormal_volume"] = 1.0 if sentiment.abnormal_news_volume else 0.0

    # 6. Benchmark Context (Relative Strength)
    if benchmark_observations and len(benchmark_observations) >= 5:
        bench_sorted = sorted(benchmark_observations, key=lambda x: x.event_time)
        bench_ret_5d = (bench_sorted[-1].close - bench_sorted[-5].close) / bench_sorted[-5].close
        feats["benchmark_return_5d"] = float(bench_ret_5d)
        feats["relative_strength_5d"] = feats["return_5d"] - float(bench_ret_5d)
    else:
        feats["benchmark_return_5d"] = 0.0
        feats["relative_strength_5d"] = feats["return_5d"]

    # Round feature values for determinism
    rounded_feats = {k: round(float(v), 5) for k, v in feats.items()}
    sorted_keys = sorted(rounded_feats.keys())

    return ResearchFeatures(
        symbol=symbol,
        as_of=normalize_datetime(as_of),
        features=rounded_feats,
        feature_schema_version="v1",
        feature_names=sorted_keys,
    )
