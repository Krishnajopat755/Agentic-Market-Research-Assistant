"""Unit tests for deterministic technical indicators."""

from datetime import UTC, datetime, timedelta

import pytest

from src.contracts.market import MarketObservation
from src.finance_core.indicators.technical import compute_technical_indicators


@pytest.fixture
def sample_bars():
    base_time = datetime(2026, 9, 25, 16, 0, tzinfo=UTC)
    bars = []
    # 60 synthetic bars with steady upward trend
    for i in range(60):
        dt = base_time - timedelta(days=59 - i)
        price = 100.0 + (i * 0.5)
        bars.append(
            MarketObservation(
                symbol="AAPL",
                event_time=dt,
                retrieved_at=dt,
                as_of=base_time,
                open=price - 0.2,
                high=price + 0.8,
                low=price - 0.5,
                close=price,
                volume=10_000_000 + (i * 100_000),
                source="fixture",
            )
        )
    return bars


def test_technical_indicators_calculation(sample_bars):
    cutoff = datetime(2026, 9, 25, 16, 10, tzinfo=UTC)
    tech = compute_technical_indicators("AAPL", sample_bars, as_of=cutoff)

    assert tech.symbol == "AAPL"
    assert tech.price == 100.0 + (59 * 0.5)
    assert tech.sma_20 is not None
    assert tech.sma_50 is not None
    assert tech.ema_20 is not None
    assert tech.rsi_14 is not None
    # Upward trending series should have RSI > 50
    assert tech.rsi_14 > 50.0
    assert tech.macd is not None
    assert tech.atr_14 is not None
    assert tech.realized_volatility_20 is not None
    assert tech.returns_1d is not None
    assert tech.returns_5d is not None
    assert tech.returns_20d is not None


def test_future_observations_excluded(sample_bars):
    """Verify observations strictly after as_of are completely ignored."""
    cutoff = datetime(2026, 9, 15, 16, 0, tzinfo=UTC)
    tech = compute_technical_indicators("AAPL", sample_bars, as_of=cutoff)

    # Latest price in indicator must match bar at cutoff, not end of sample_bars
    valid_bars = [b for b in sample_bars if b.event_time <= cutoff]
    assert tech.price == valid_bars[-1].close
