"""Unit tests for news normalization and deduplication."""

from datetime import UTC, datetime

from src.contracts.news import NewsArticle
from src.finance_core.news.deduplication import deduplicate_news
from src.finance_core.news.normalization import canonicalize_url, generate_article_id


def test_canonicalize_url():
    raw_url = "https://www.bloomberg.com/news/articles/apple-event?utm_source=twitter&ref=newsletter#section2"
    canon = canonicalize_url(raw_url)
    assert canon == "https://bloomberg.com/news/articles/apple-event"
    assert "utm_source" not in canon
    assert "#section2" not in canon


def test_article_id_stability():
    id1 = generate_article_id("https://ft.com/apple", "Apple Beats Revenue Forecast")
    id2 = generate_article_id("https://ft.com/apple", "apple beats revenue forecast!")
    assert id1 == id2


def test_deduplicate_news():
    now = datetime(2026, 9, 25, 12, 0, tzinfo=UTC)
    art1 = NewsArticle(
        article_id="art-1",
        provider_article_id="p-101",
        publisher="Reuters",
        title="Apple Reports Q4 Record Services Growth",
        description="Services revenue rose 14% year over year.",
        article_url="https://reuters.com/apple-q4",
        published_at=now,
        retrieved_at=now,
        tickers=["AAPL"],
        source_provider="alphavantage",
    )

    # Identical provider ID
    art2 = NewsArticle(
        article_id="art-2",
        provider_article_id="p-101",
        publisher="Yahoo Finance (Wire)",
        title="Apple Reports Q4 Record Services Growth",
        description="Services revenue rose 14% year over year.",
        article_url="https://finance.yahoo.com/apple-wire",
        published_at=now,
        retrieved_at=now,
        tickers=["AAPL"],
        source_provider="alphavantage",
    )

    # Distinct article
    art3 = NewsArticle(
        article_id="art-3",
        provider_article_id="p-102",
        publisher="WSJ",
        title="Federal Reserve Holds Interest Rates Steady",
        description="Central bank maintains current policy rate.",
        article_url="https://wsj.com/fed-decision",
        published_at=now,
        retrieved_at=now,
        tickers=["SPY"],
        source_provider="alphavantage",
    )

    canonical, all_tagged = deduplicate_news([art1, art2, art3])

    assert len(canonical) == 2
    assert len(all_tagged) == 3

    assert all_tagged[0].is_duplicate is False
    assert all_tagged[1].is_duplicate is True
    assert all_tagged[1].duplicate_group_id == all_tagged[0].duplicate_group_id
    assert "Exact provider article ID" in (all_tagged[1].duplicate_reason or "")
