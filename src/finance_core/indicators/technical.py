"""Deterministic technical indicators computed strictly point-in-time."""

from collections.abc import Sequence
from datetime import datetime

import numpy as np
import pandas as pd

from src.contracts.errors import ErrorCode, FinanceAppException
from src.contracts.market import MarketObservation
from src.contracts.technical import TechnicalSnapshot
from src.finance_core.market_data.normalization import (
    filter_market_observations_point_in_time,
    normalize_datetime,
)


def compute_technical_indicators(
    symbol: str,
    observations: Sequence[MarketObservation],
    as_of: datetime,
) -> TechnicalSnapshot:
    """
    Compute deterministic technical indicators strictly using data up to as_of.
    Observations are filtered point-in-time and sorted chronologically.
    """
    valid_obs = filter_market_observations_point_in_time(observations, as_of)
    if len(valid_obs) < 5:
        raise FinanceAppException(
            error_code=ErrorCode.EMPTY_RESULT,
            message=f"Insufficient history ({len(valid_obs)} bars) to compute indicators for {symbol}",
        )

    # Convert to DataFrame
    df = pd.DataFrame([obs.model_dump() for obs in valid_obs])
    df.sort_values(by="event_time", inplace=True)
    df.reset_index(drop=True, inplace=True)

    closes = df["close"]
    highs = df["high"]
    lows = df["low"]
    volumes = df["volume"]
    n = len(df)

    latest_price = float(closes.iloc[-1])

    # 1. Moving Averages
    sma_20 = float(closes.rolling(window=20).mean().iloc[-1]) if n >= 20 else None
    sma_50 = float(closes.rolling(window=50).mean().iloc[-1]) if n >= 50 else None
    ema_20 = float(closes.ewm(span=20, adjust=False).mean().iloc[-1]) if n >= 20 else None

    # 2. RSI (14-period)
    rsi_14 = None
    if n >= 15:
        delta = closes.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        last_gain = float(avg_gain.iloc[-1])
        last_loss = float(avg_loss.iloc[-1])
        if np.isnan(last_gain) or np.isnan(last_loss):
            rsi_14 = 50.0
        elif last_loss == 0.0:
            rsi_14 = 100.0 if last_gain > 0 else 50.0
        elif last_gain == 0.0:
            rsi_14 = 0.0
        else:
            rs = last_gain / last_loss
            rsi_14 = float(100.0 - (100.0 / (1.0 + rs)))

    # 3. MACD (12, 26, 9)
    macd_val = None
    macd_signal = None
    macd_hist = None
    if n >= 26:
        ema12 = closes.ewm(span=12, adjust=False).mean()
        ema26 = closes.ewm(span=26, adjust=False).mean()
        macd_line = ema12 - ema26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        hist = macd_line - signal_line
        macd_val = float(macd_line.iloc[-1])
        macd_signal = float(signal_line.iloc[-1])
        macd_hist = float(hist.iloc[-1])

    # 4. ATR (14-period)
    atr_14 = None
    if n >= 15:
        prev_close = closes.shift(1)
        tr1 = highs - lows
        tr2 = (highs - prev_close).abs()
        tr3 = (lows - prev_close).abs()
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr_series = true_range.rolling(window=14).mean()
        val = atr_series.iloc[-1]
        atr_14 = float(val) if not np.isnan(val) else None

    # 5. Realized Volatility (20-day annualized)
    realized_vol_20 = None
    if n >= 21:
        log_ret = np.log(closes / closes.shift(1))
        vol_20 = log_ret.rolling(window=20).std() * np.sqrt(252)
        val = vol_20.iloc[-1]
        realized_vol_20 = float(val) if not np.isnan(val) else None

    # 6. Volume Z-Score (20-day)
    volume_zscore_20 = None
    if n >= 20:
        vol_mean = volumes.rolling(window=20).mean()
        vol_std = volumes.rolling(window=20).std().replace(0, np.nan)
        zscore = (volumes - vol_mean) / vol_std
        val = zscore.iloc[-1]
        volume_zscore_20 = float(val) if not np.isnan(val) else 0.0

    # 7. Returns
    ret_1d = float(closes.pct_change(1).iloc[-1]) if n >= 2 else None
    ret_5d = float(closes.pct_change(5).iloc[-1]) if n >= 6 else None
    ret_20d = float(closes.pct_change(20).iloc[-1]) if n >= 21 else None

    return TechnicalSnapshot(
        symbol=symbol,
        as_of=normalize_datetime(as_of),
        price=round(latest_price, 4),
        sma_20=round(sma_20, 4) if sma_20 is not None else None,
        sma_50=round(sma_50, 4) if sma_50 is not None else None,
        ema_20=round(ema_20, 4) if ema_20 is not None else None,
        rsi_14=round(rsi_14, 4) if rsi_14 is not None else None,
        macd=round(macd_val, 4) if macd_val is not None else None,
        macd_signal=round(macd_signal, 4) if macd_signal is not None else None,
        macd_hist=round(macd_hist, 4) if macd_hist is not None else None,
        atr_14=round(atr_14, 4) if atr_14 is not None else None,
        realized_volatility_20=round(realized_vol_20, 4) if realized_vol_20 is not None else None,
        volume_zscore_20=round(volume_zscore_20, 4) if volume_zscore_20 is not None else None,
        returns_1d=round(ret_1d, 4) if ret_1d is not None else None,
        returns_5d=round(ret_5d, 4) if ret_5d is not None else None,
        returns_20d=round(ret_20d, 4) if ret_20d is not None else None,
    )
