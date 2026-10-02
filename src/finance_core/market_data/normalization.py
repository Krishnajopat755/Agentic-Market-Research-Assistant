"""Market data normalization and point-in-time filtering."""

from collections.abc import Sequence
from datetime import UTC, datetime

from src.contracts.errors import ErrorCode, FinanceAppException
from src.contracts.market import MarketObservation, MarketSnapshot


def normalize_datetime(dt: datetime | str) -> datetime:
    """Normalize datetime to UTC."""
    if isinstance(dt, str):
        # Handle trailing Z or offsets
        dt_str = dt.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(dt_str)
    else:
        parsed = dt

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def filter_market_observations_point_in_time(
    observations: Sequence[MarketObservation],
    as_of: datetime,
    stale_market_seconds: int = 1800,
) -> list[MarketObservation]:
    """
    Enforce point-in-time correctness:
    Exclude any observations where event_time > as_of or retrieved_at > as_of (for historical backtest).
    Calculates freshness and staleness flags.
    """
    as_of_utc = normalize_datetime(as_of)
    valid_observations: list[MarketObservation] = []

    for obs in observations:
        event_time_utc = normalize_datetime(obs.event_time)
        if event_time_utc > as_of_utc:
            # Strictly reject future observations (Rule 2)
            continue

        freshness_secs = max(0.0, (as_of_utc - event_time_utc).total_seconds())
        is_stale = freshness_secs > stale_market_seconds

        updated_obs = obs.model_copy(
            update={
                "event_time": event_time_utc,
                "as_of": as_of_utc,
                "freshness_seconds": freshness_secs,
                "is_stale": is_stale,
            }
        )
        valid_observations.append(updated_obs)

    # Sort strictly chronologically
    valid_observations.sort(key=lambda x: x.event_time)
    return valid_observations


def build_market_snapshot(
    symbol: str,
    observations: Sequence[MarketObservation],
    as_of: datetime,
    stale_market_seconds: int = 1800,
    source: str = "alphavantage",
) -> MarketSnapshot:
    """Build a market snapshot from the latest valid point-in-time observation."""
    valid_obs = filter_market_observations_point_in_time(observations, as_of, stale_market_seconds)
    if not valid_obs:
        raise FinanceAppException(
            error_code=ErrorCode.EMPTY_RESULT,
            message=f"No valid point-in-time market observations for symbol '{symbol}' as of {as_of.isoformat()}",
        )

    latest = valid_obs[-1]
    prev_close = valid_obs[-2].close if len(valid_obs) >= 2 else latest.open
    price = latest.close
    change = price - prev_close
    change_pct = (change / prev_close * 100.0) if prev_close > 0 else 0.0

    return MarketSnapshot(
        symbol=symbol,
        timestamp=latest.event_time,
        price=price,
        change=round(change, 4),
        change_percent=round(change_pct, 4),
        volume=latest.volume,
        open=latest.open,
        high=latest.high,
        low=latest.low,
        prev_close=prev_close,
        source=source,
        retrieved_at=latest.retrieved_at,
        as_of=normalize_datetime(as_of),
        is_stale=latest.is_stale,
        freshness_seconds=latest.freshness_seconds,
    )
