"""Abstract base interfaces for market and news providers."""

from abc import ABC, abstractmethod
from datetime import datetime

from src.contracts.market import MarketCalendar, MarketObservation, MarketSnapshot
from src.contracts.mcp import ProviderHealth
from src.contracts.news import NewsArticle


class BaseMarketDataProvider(ABC):
    """Abstract interface for market data retrieval."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider e.g. alphavantage, polygon, fixture."""

    @abstractmethod
    async def resolve_symbol(self, symbol: str) -> dict[str, str]:
        """Validate and resolve symbol to canonical identifier, name, exchange."""

    @abstractmethod
    async def get_snapshot(self, symbol: str, as_of: datetime) -> MarketSnapshot:
        """Fetch latest snapshot quote as of cutoff T."""

    @abstractmethod
    async def get_historical_bars(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        interval: str = "daily",
    ) -> list[MarketObservation]:
        """Fetch historical OHLCV bars strictly within [start, end]."""

    @abstractmethod
    async def get_benchmark(
        self,
        symbol: str = "SPY",
        start: datetime | None = None,
        end: datetime | None = None,
        interval: str = "daily",
    ) -> list[MarketObservation]:
        """Fetch benchmark (e.g. SPY or QQQ) historical bars."""

    @abstractmethod
    async def get_calendar(self, as_of: datetime) -> MarketCalendar:
        """Get market trading session state as of cutoff T."""

    @abstractmethod
    async def get_health(self) -> ProviderHealth:
        """Check provider connectivity, latency, and rate limits."""


class BaseNewsProvider(ABC):
    """Abstract interface for news retrieval."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    async def get_news(
        self,
        symbols: list[str],
        start: datetime,
        end: datetime,
        limit: int = 50,
    ) -> list[NewsArticle]:
        """Fetch news articles published within [start, end] for symbols."""

    @abstractmethod
    async def get_health(self) -> ProviderHealth:
        pass
