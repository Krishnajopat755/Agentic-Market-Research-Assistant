"""Mandatory Point-in-time correctness and lookahead bias verification suite (Rule 2)."""

import json
from datetime import UTC, datetime

from src.contracts.market import MarketObservation
from src.contracts.news import NewsArticle
from src.finance_core.evaluation.leakage_detector import verify_lookahead_bias


def test_mandatory_lookahead_bias_prevention():
    """
    Verify that injecting future market spikes or future news strictly after
    analysis cutoff T produces zero change to indicators, features, or signal at T.
    """
    cutoff = datetime(2026, 9, 25, 16, 10, 0, tzinfo=UTC)

    # 1. Load clean historical bars up to T
    with open("fixtures/point_in_time/AAPL_cutoff_t.json", "r", encoding="utf-8") as f:
        hist_bars = [MarketObservation(**item) for item in json.load(f)]

    # 2. Load future tampered bars (includes future bars on Sep 28 and Sep 29)
    with open("fixtures/point_in_time/AAPL_future_tampered.json", "r", encoding="utf-8") as f:
        tampered_bars = [MarketObservation(**item) for item in json.load(f)]

    # 3. Load historical news
    with open("fixtures/news/AAPL_news.json", "r", encoding="utf-8") as f:
        hist_news = [NewsArticle(**item) for item in json.load(f)]

    # 4. Tampered news: inject future breaking news published on Sep 28
    tampered_news = list(hist_news)
    tampered_news.append(
        NewsArticle(
            article_id="future-art-999",
            publisher="Future Wire",
            title="Apple Declares Massive Special Dividend on Future Date",
            description="Future event that should not be visible at cutoff T.",
            article_url="https://future.example.com/apple",
            published_at=datetime(2026, 9, 28, 10, 0, 0, tzinfo=UTC),
            retrieved_at=datetime(2026, 9, 28, 10, 0, 0, tzinfo=UTC),
            available_at=datetime(2026, 9, 28, 10, 0, 0, tzinfo=UTC),
            tickers=["AAPL"],
            source_provider="fixture",
        )
    )

    # Run verification suite: must pass with zero differences
    checks = verify_lookahead_bias(
        symbol="AAPL",
        as_of=cutoff,
        historical_market_bars=hist_bars,
        future_tampered_market_bars=tampered_bars,
        historical_news=hist_news,
        future_tampered_news=tampered_news,
    )

    for check_name, passed in checks.items():
        assert passed is True, f"Check {check_name} failed: point-in-time leakage detected!"
