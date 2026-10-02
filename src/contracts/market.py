"""Market data contracts including observations, snapshots, and calendar."""

from datetime import datetime

from pydantic import BaseModel, Field


class MarketObservation(BaseModel):
    """Normalized OHLCV bar with rigorous point-in-time provenance."""

    symbol: str
    event_time: datetime = Field(..., description="Timestamp of the bar close")
    retrieved_at: datetime = Field(..., description="Timestamp when observation was retrieved")
    as_of: datetime = Field(..., description="Analysis cutoff timestamp")
    open: float = Field(..., ge=0.0)
    high: float = Field(..., ge=0.0)
    low: float = Field(..., ge=0.0)
    close: float = Field(..., ge=0.0)
    volume: float = Field(..., ge=0.0)
    source: str = Field(default="alphavantage")
    provider_record_id: str | None = None
    entitlement: str = Field(default="delayed", description="realtime, delayed, or eod")
    artifact_ref: str | None = None
    is_stale: bool = False
    freshness_seconds: float = 0.0


class MarketSnapshot(BaseModel):
    """Latest market quote and session state as of the cutoff."""

    symbol: str
    timestamp: datetime
    price: float = Field(..., ge=0.0)
    change: float = 0.0
    change_percent: float = 0.0
    volume: float = Field(default=0.0, ge=0.0)
    open: float = Field(default=0.0, ge=0.0)
    high: float = Field(default=0.0, ge=0.0)
    low: float = Field(default=0.0, ge=0.0)
    prev_close: float = Field(default=0.0, ge=0.0)
    source: str = "alphavantage"
    retrieved_at: datetime
    as_of: datetime
    is_stale: bool = False
    freshness_seconds: float = 0.0


class MarketCalendar(BaseModel):
    """Trading session and calendar metadata."""

    market: str = "US"
    is_open: bool
    session_open: datetime | None = None
    session_close: datetime | None = None
    next_open: datetime | None = None
    next_close: datetime | None = None
