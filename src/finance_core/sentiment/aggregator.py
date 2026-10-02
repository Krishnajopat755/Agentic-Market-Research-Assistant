"""Aggregate sentiment computation across a deduplicated news set."""

from collections.abc import Sequence
from datetime import datetime

import numpy as np

from src.contracts.news import AggregateSentiment, NewsArticle
from src.finance_core.market_data.normalization import normalize_datetime


def aggregate_sentiment(
    symbol: str,
    articles: Sequence[NewsArticle],
    as_of: datetime,
    historical_baseline_count: int = 5,
) -> AggregateSentiment:
    """
    Compute aggregate sentiment metrics for a symbol as of cutoff T.
    Considers only unique/canonical articles (ignores duplicates).
    """
    as_of_utc = normalize_datetime(as_of)
    # Filter to non-duplicate articles tagged with symbol
    valid_articles = [
        a
        for a in articles
        if not a.is_duplicate
        and (not a.tickers or symbol.upper() in [t.upper() for t in a.tickers])
    ]

    if not valid_articles:
        return AggregateSentiment(
            symbol=symbol,
            as_of=as_of_utc,
            article_count=0,
            mean_score=0.0,
            median_score=0.0,
            sentiment_dispersion=0.0,
            positive_share=0.0,
            negative_share=0.0,
            neutral_share=0.0,
            sentiment_change=0.0,
            abnormal_news_volume=False,
            source_diversity=0,
        )

    scores: list[float] = []
    labels: list[str] = []
    publishers: set[str] = set()

    for a in valid_articles:
        publishers.add(a.publisher)
        if a.sentiment:
            scores.append(a.sentiment.score)
            labels.append(a.sentiment.label)
        else:
            scores.append(0.0)
            labels.append("neutral")

    count = len(scores)
    mean_val = float(np.mean(scores))
    median_val = float(np.median(scores))
    dispersion = float(np.std(scores)) if count > 1 else 0.0

    pos_count = sum(1 for lbl in labels if lbl == "positive")
    neg_count = sum(1 for lbl in labels if lbl == "negative")
    neu_count = sum(1 for lbl in labels if lbl == "neutral")

    pos_share = pos_count / count
    neg_share = neg_count / count
    neu_share = neu_count / count

    # Sentiment change proxy: compare first half of time window with second half
    if count >= 4:
        # sorted by published_at ascending
        sorted_articles = sorted(valid_articles, key=lambda x: x.published_at)
        mid = count // 2
        earlier_scores = [a.sentiment.score for a in sorted_articles[:mid] if a.sentiment]
        recent_scores = [a.sentiment.score for a in sorted_articles[mid:] if a.sentiment]
        earlier_mean = float(np.mean(earlier_scores)) if earlier_scores else 0.0
        recent_mean = float(np.mean(recent_scores)) if recent_scores else 0.0
        sentiment_change = recent_mean - earlier_mean
    else:
        sentiment_change = 0.0

    abnormal_vol = count >= (historical_baseline_count * 2)

    return AggregateSentiment(
        symbol=symbol,
        as_of=as_of_utc,
        article_count=count,
        mean_score=round(mean_val, 4),
        median_score=round(median_val, 4),
        sentiment_dispersion=round(dispersion, 4),
        positive_share=round(pos_share, 4),
        negative_share=round(neg_share, 4),
        neutral_share=round(neu_share, 4),
        sentiment_change=round(sentiment_change, 4),
        abnormal_news_volume=abnormal_vol,
        source_diversity=len(publishers),
    )
