"""Unit tests for financial sentiment and aggregation."""

from datetime import UTC, datetime

from src.contracts.news import NewsArticle
from src.finance_core.sentiment.aggregator import aggregate_sentiment
from src.finance_core.sentiment.dictionary import FinancialLexiconSentimentModel


def test_lexicon_positive_sentiment():
    model = FinancialLexiconSentimentModel()
    text = "Apple posted record profits, beating revenue guidance with strong iPhone growth and dividend expansion."
    score = model.score(text)
    assert score.label == "positive"
    assert score.score > 0.3


def test_lexicon_negative_sentiment():
    model = FinancialLexiconSentimentModel()
    text = "Company plunged after severe earnings miss, reporting massive losses, layoffs, and regulatory investigation."
    score = model.score(text)
    assert score.label == "negative"
    assert score.score < -0.3


def test_negation_handling():
    model = FinancialLexiconSentimentModel()
    text = "The firm did not miss targets and showed no losses during the quarter."
    score = model.score(text)
    # Negating "miss" and "losses" should not produce a strongly negative score
    assert score.label != "negative"


def test_aggregate_sentiment():
    now = datetime(2026, 9, 25, 12, 0, tzinfo=UTC)
    model = FinancialLexiconSentimentModel()

    articles = [
        NewsArticle(
            article_id="a1",
            publisher="Bloomberg",
            title="Apple surge as profits beat estimates",
            article_url="https://bloomberg.com/a1",
            published_at=now,
            retrieved_at=now,
            tickers=["AAPL"],
            source_provider="fixture",
            sentiment=model.score("Apple surge as profits beat estimates"),
        ),
        NewsArticle(
            article_id="a2",
            publisher="Reuters",
            title="Apple expansion in cloud infrastructure",
            article_url="https://reuters.com/a2",
            published_at=now,
            retrieved_at=now,
            tickers=["AAPL"],
            source_provider="fixture",
            sentiment=model.score("Apple expansion in cloud infrastructure"),
        ),
    ]

    agg = aggregate_sentiment("AAPL", articles, as_of=now)
    assert agg.article_count == 2
    assert agg.mean_score > 0.0
    assert agg.source_diversity == 2
