"""Unit tests for deterministic scorecard signal model."""

from datetime import UTC, datetime

from src.contracts.features import ResearchFeatures
from src.finance_core.signal.scorecard import compute_scorecard_signal


def test_bullish_scorecard():
    now = datetime(2026, 9, 25, 16, 0, tzinfo=UTC)
    features = ResearchFeatures(
        symbol="AAPL",
        as_of=now,
        features={
            "return_5d": 0.04,  # +4% momentum
            "dist_sma_50": 0.08,  # well above 50d SMA
            "rsi_norm": 0.35,  # bullish RSI ~ 67.5
            "macd_hist_norm": 0.005,  # positive MACD expansion
            "news_mean_sentiment": 0.45,  # positive news
            "news_sentiment_change": 0.20,
            "volume_zscore": 1.5,
            "volatility_20d": 0.18,  # healthy low volatility
            "news_article_count": 5.0,
        },
    )

    sig = compute_scorecard_signal(features)
    assert sig.symbol == "AAPL"
    assert sig.state == "BULLISH"
    assert sig.score > 0.20
    assert sig.confidence > 0.60
    assert len(sig.top_contributors) > 0


def test_bearish_scorecard():
    now = datetime(2026, 9, 25, 16, 0, tzinfo=UTC)
    features = ResearchFeatures(
        symbol="XYZ",
        as_of=now,
        features={
            "return_5d": -0.06,
            "dist_sma_50": -0.12,
            "rsi_norm": -0.40,
            "macd_hist_norm": -0.008,
            "news_mean_sentiment": -0.50,
            "news_sentiment_change": -0.30,
            "volume_zscore": 2.0,
            "volatility_20d": 0.45,
            "news_article_count": 8.0,
        },
    )

    sig = compute_scorecard_signal(features)
    assert sig.state == "BEARISH"
    assert sig.score < -0.20
