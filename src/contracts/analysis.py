"""AnalysisRequest data contract."""

from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    """Input research request specifying universe, timestamp cutoff, and parameters."""

    run_id: str = Field(default_factory=lambda: str(uuid4()))
    symbols: list[str] = Field(
        ..., min_length=1, description="Watchlist symbols e.g. ['AAPL', 'MSFT']"
    )
    analysis_timestamp: datetime = Field(
        ..., description="Target point-in-time cutoff in RFC3339/ISO format"
    )
    timezone: str = Field(default="America/New_York", description="Market timezone")
    market: str = Field(default="US", description="Market jurisdiction e.g. US")
    price_lookback_days: int = Field(
        default=120, ge=10, le=1000, description="OHLCV history lookback in calendar days"
    )
    news_lookback_hours: int = Field(
        default=24, ge=1, le=720, description="News history lookback in hours"
    )
    signal_horizon_bars: int = Field(
        default=5, ge=1, le=60, description="Prediction horizon in bars"
    )
    sentiment_model: str = Field(
        default="finance_sentiment_default", description="Sentiment model identity"
    )
    stale_market_seconds: int = Field(
        default=1800, ge=60, description="Threshold after which snapshot is considered stale"
    )
    stale_news_seconds: int = Field(
        default=7200, ge=60, description="Threshold after which news stream is considered stale"
    )
