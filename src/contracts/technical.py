"""Technical analysis indicators snapshot contract."""

from datetime import datetime

from pydantic import BaseModel


class TechnicalSnapshot(BaseModel):
    """Snapshot of technical indicator values calculated strictly as of cutoff T."""

    symbol: str
    as_of: datetime
    price: float
    sma_20: float | None = None
    sma_50: float | None = None
    ema_20: float | None = None
    rsi_14: float | None = None
    macd: float | None = None
    macd_signal: float | None = None
    macd_hist: float | None = None
    atr_14: float | None = None
    realized_volatility_20: float | None = None
    volume_zscore_20: float | None = None
    returns_1d: float | None = None
    returns_5d: float | None = None
    returns_20d: float | None = None
