"""Deterministic fixture provider for offline testing and CI verification."""

import json
from datetime import UTC, datetime
from pathlib import Path

from src.contracts.errors import ErrorCode, FinanceAppException
from src.contracts.market import MarketCalendar, MarketObservation, MarketSnapshot
from src.contracts.mcp import ProviderHealth
from src.contracts.news import NewsArticle
from src.finance_core.market_data.normalization import (
    build_market_snapshot,
    filter_market_observations_point_in_time,
    normalize_datetime,
)
from src.finance_core.news.normalization import filter_news_point_in_time
from src.providers.base import BaseMarketDataProvider, BaseNewsProvider

KNOWN_SYMBOLS = {
    "AAPL": {"name": "Apple Inc.", "exchange": "NASDAQ", "currency": "USD"},
    "MSFT": {"name": "Microsoft Corporation", "exchange": "NASDAQ", "currency": "USD"},
    "NVDA": {"name": "NVIDIA Corporation", "exchange": "NASDAQ", "currency": "USD"},
    "SPY": {"name": "SPDR S&P 500 ETF Trust", "exchange": "NYSE Arca", "currency": "USD"},
}


class FixtureMarketDataProvider(BaseMarketDataProvider):
    """Market data provider backed by deterministic JSON fixtures."""

    def __init__(
        self,
        fixtures_dir: str | Path = "fixtures/market",
        simulate_failure_code: ErrorCode | None = None,
        simulate_failure_count: int = 0,
    ):
        self._fixtures_dir = Path(fixtures_dir)
        self.simulate_failure_code = simulate_failure_code
        self.failure_counter = simulate_failure_count
        self.call_count = 0

    @property
    def provider_name(self) -> str:
        return "fixture_market_provider"

    def _maybe_simulate_failure(self) -> None:
        self.call_count += 1
        if self.simulate_failure_code and self.failure_counter > 0:
            self.failure_counter -= 1
            if self.simulate_failure_code == ErrorCode.RATE_LIMITED:
                raise FinanceAppException(
                    error_code=ErrorCode.RATE_LIMITED,
                    message="Provider rate limit reached (simulated fixture error).",
                    retryable=True,
                    retry_after_seconds=1,
                )
            elif self.simulate_failure_code == ErrorCode.PROVIDER_UNAVAILABLE:
                raise FinanceAppException(
                    error_code=ErrorCode.PROVIDER_UNAVAILABLE,
                    message="Market data provider temporarily unavailable (simulated fixture error).",
                    retryable=True,
                    retry_after_seconds=1,
                )
            else:
                raise FinanceAppException(
                    error_code=self.simulate_failure_code,
                    message=f"Simulated fixture failure: {self.simulate_failure_code}",
                )

    async def resolve_symbol(self, symbol: str) -> dict[str, str]:
        self._maybe_simulate_failure()
        sym = symbol.upper().strip()
        if sym in KNOWN_SYMBOLS:
            info = KNOWN_SYMBOLS[sym]
            return {
                "symbol": sym,
                "name": info["name"],
                "exchange": info["exchange"],
                "currency": info["currency"],
            }
        raise FinanceAppException(
            error_code=ErrorCode.INVALID_SYMBOL,
            message=f"Unknown or unsupported equity symbol '{symbol}'",
        )

    def _load_raw_bars(self, symbol: str) -> list[MarketObservation]:
        filepath = self._fixtures_dir / f"{symbol.upper()}_daily.json"
        if not filepath.exists():
            raise FinanceAppException(
                error_code=ErrorCode.EMPTY_RESULT,
                message=f"No fixture data found for symbol '{symbol}' at {filepath}",
            )
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [MarketObservation(**item) for item in data]

    async def get_historical_bars(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        interval: str = "daily",
    ) -> list[MarketObservation]:
        self._maybe_simulate_failure()
        raw_bars = self._load_raw_bars(symbol)
        start_utc = normalize_datetime(start)
        end_utc = normalize_datetime(end)

        # Filter strictly within [start, end]
        bars = [b for b in raw_bars if start_utc <= normalize_datetime(b.event_time) <= end_utc]
        return filter_market_observations_point_in_time(bars, as_of=end_utc)

    async def get_snapshot(self, symbol: str, as_of: datetime) -> MarketSnapshot:
        self._maybe_simulate_failure()
        raw_bars = self._load_raw_bars(symbol)
        return build_market_snapshot(symbol, raw_bars, as_of=as_of, source="alphavantage_fixture")

    async def get_benchmark(
        self,
        symbol: str = "SPY",
        start: datetime | None = None,
        end: datetime | None = None,
        interval: str = "daily",
    ) -> list[MarketObservation]:
        self._maybe_simulate_failure()
        raw_bars = self._load_raw_bars(symbol)
        end_dt = end or datetime.now(UTC)
        return filter_market_observations_point_in_time(raw_bars, as_of=end_dt)

    async def get_calendar(self, as_of: datetime) -> MarketCalendar:
        self._maybe_simulate_failure()
        as_of_utc = normalize_datetime(as_of)
        is_weekday = as_of_utc.weekday() < 5
        return MarketCalendar(
            market="US",
            is_open=is_weekday and (9 <= as_of_utc.hour < 16),
            session_open=as_of_utc.replace(hour=9, minute=30, second=0),
            session_close=as_of_utc.replace(hour=16, minute=0, second=0),
        )

    async def get_health(self) -> ProviderHealth:
        return ProviderHealth(
            provider_name=self.provider_name,
            is_healthy=True,
            latency_ms=2.5,
            rate_limit_remaining=500,
            rate_limit_reset_seconds=60,
            message="Fixture provider active",
        )


class FixtureNewsProvider(BaseNewsProvider):
    """News provider backed by deterministic JSON fixtures."""

    def __init__(
        self,
        fixtures_dir: str | Path = "fixtures/news",
        simulate_failure_code: ErrorCode | None = None,
        simulate_failure_count: int = 0,
    ):
        self._fixtures_dir = Path(fixtures_dir)
        self.simulate_failure_code = simulate_failure_code
        self.failure_counter = simulate_failure_count

    @property
    def provider_name(self) -> str:
        return "fixture_news_provider"

    def _maybe_simulate_failure(self) -> None:
        if self.simulate_failure_code and self.failure_counter > 0:
            self.failure_counter -= 1
            if self.simulate_failure_code == ErrorCode.RATE_LIMITED:
                raise FinanceAppException(
                    error_code=ErrorCode.RATE_LIMITED,
                    message="News provider rate limit reached (simulated fixture error).",
                    retryable=True,
                    retry_after_seconds=1,
                )
            raise FinanceAppException(
                error_code=self.simulate_failure_code,
                message=f"Simulated fixture failure: {self.simulate_failure_code}",
            )

    async def get_news(
        self,
        symbols: list[str],
        start: datetime,
        end: datetime,
        limit: int = 50,
    ) -> list[NewsArticle]:
        self._maybe_simulate_failure()
        all_articles: list[NewsArticle] = []

        for symbol in symbols:
            filepath = self._fixtures_dir / f"{symbol.upper()}_news.json"
            if filepath.exists():
                with open(filepath, "r", encoding="utf-8") as f:
                    items = json.load(f)
                all_articles.extend([NewsArticle(**item) for item in items])

        # Filter strictly point-in-time
        return filter_news_point_in_time(all_articles, as_of=end)[:limit]

    async def get_health(self) -> ProviderHealth:
        return ProviderHealth(
            provider_name=self.provider_name,
            is_healthy=True,
            latency_ms=3.1,
            rate_limit_remaining=100,
            rate_limit_reset_seconds=60,
            message="Fixture news provider active",
        )
