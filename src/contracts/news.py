"""News and sentiment data contracts."""

from datetime import datetime

from pydantic import BaseModel, Field


class SentimentScore(BaseModel):
    """Sentiment classification and scalar score."""

    label: str = Field(..., description="positive, neutral, or negative")
    score: float = Field(..., ge=-1.0, le=1.0, description="Normalized score in [-1.0, 1.0]")
    model: str = Field(..., description="Identifier and version of the scoring model")
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    explanation: str | None = None


class NewsArticle(BaseModel):
    """Normalized news article with deduplication tracking and provenance."""

    article_id: str = Field(
        ..., description="Stable SHA-256 hash derived from canonical URL + title"
    )
    provider_article_id: str | None = None
    publisher: str
    title: str
    description: str | None = None
    article_url: str
    published_at: datetime
    retrieved_at: datetime
    available_at: datetime | None = None
    tickers: list[str] = Field(default_factory=list)
    source_provider: str
    duplicate_group_id: str | None = None
    is_duplicate: bool = False
    duplicate_reason: str | None = None
    sentiment: SentimentScore | None = None
    is_stale: bool = False
    freshness_seconds: float = 0.0


class AggregateSentiment(BaseModel):
    """Aggregated sentiment statistics across a deduplicated news set."""

    symbol: str
    as_of: datetime
    article_count: int = 0
    mean_score: float = 0.0
    median_score: float = 0.0
    sentiment_dispersion: float = 0.0
    positive_share: float = 0.0
    negative_share: float = 0.0
    neutral_share: float = 0.0
    sentiment_change: float = 0.0
    abnormal_news_volume: bool = False
    source_diversity: int = 0
