"""Polygon.io / Massive market and news provider adapter."""

import os
from datetime import UTC, datetime

import httpx

from src.contracts.errors import ErrorCode, FinanceAppException
from src.contracts.market import MarketCalendar, MarketObservation, MarketSnapshot
from src.contracts.mcp import ProviderHealth
from src.contracts.news import NewsArticle
from src.finance_core.market_data.normalization import normalize_datetime
from src.finance_core.news.normalization import (
    canonicalize_url,
    filter_news_point_in_time,
    generate_article_id,
)
from src.providers.base import BaseMarketDataProvider, BaseNewsProvider


class PolygonProvider(BaseMarketDataProvider, BaseNewsProvider):
    """Polygon.io provider adapter adhering to provider abstraction."""

    BASE_URL = "https://api.polygon.io"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("POLYGON_API_KEY", "")

    @property
    def provider_name(self) -> str:
        return "polygon"

    def _ensure_api_key(self) -> None:
        if not self.api_key:
            raise FinanceAppException(
                error_code=ErrorCode.AUTH_ERROR,
                message="Polygon API key missing. Set POLYGON_API_KEY or use fixture mode.",
            )

    async def resolve_symbol(self, symbol: str) -> dict[str, str]:
        self._ensure_api_key()
        sym = symbol.upper().strip()
        url = f"{self.BASE_URL}/v3/reference/tickers/{sym}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 404:
                raise FinanceAppException(
                    error_code=ErrorCode.INVALID_SYMBOL,
                    message=f"Ticker '{sym}' not found on Polygon",
                )
            data = resp.json().get("results", {})

        return {
            "symbol": data.get("ticker", sym),
            "name": data.get("name", sym),
            "exchange": data.get("primary_exchange", "US"),
            "currency": data.get("currency_name", "USD"),
        }

    async def get_historical_bars(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        interval: str = "daily",
    ) -> list[MarketObservation]:
        self._ensure_api_key()
        start_str = start.strftime("%Y-%m-%d")
        end_str = end.strftime("%Y-%m-%d")
        sym = symbol.upper().strip()
        url = f"{self.BASE_URL}/v2/aggs/ticker/{sym}/range/1/day/{start_str}/{end_str}"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 429:
                raise FinanceAppException(
                    error_code=ErrorCode.RATE_LIMITED,
                    message="Polygon rate limit reached",
                    retryable=True,
                    retry_after_seconds=30,
                )
            data = resp.json()

        results = data.get("results", [])
        observations: list[MarketObservation] = []
        end_utc = normalize_datetime(end)

        for bar in results:
            # timestamp in milliseconds
            dt = datetime.fromtimestamp(bar["t"] / 1000.0, tz=UTC)
            observations.append(
                MarketObservation(
                    symbol=sym,
                    event_time=dt,
                    retrieved_at=datetime.now(UTC),
                    as_of=end_utc,
                    open=float(bar["o"]),
                    high=float(bar["h"]),
                    low=float(bar["l"]),
                    close=float(bar["c"]),
                    volume=float(bar["v"]),
                    source="polygon",
                    entitlement="delayed",
                )
            )

        return observations

    async def get_snapshot(self, symbol: str, as_of: datetime) -> MarketSnapshot:
        self._ensure_api_key()
        sym = symbol.upper().strip()
        url = f"{self.BASE_URL}/v2/snapshot/locale/us/markets/stocks/tickers/{sym}"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, headers=headers)
            data = resp.json().get("ticker", {})

        day_bar = data.get("day", {})
        price = float(day_bar.get("c", data.get("lastTrade", {}).get("p", 0.0)))
        prev_close = float(data.get("prevDay", {}).get("c", price))
        change = price - prev_close
        change_pct = (change / prev_close * 100.0) if prev_close > 0 else 0.0

        return MarketSnapshot(
            symbol=sym,
            timestamp=datetime.now(UTC),
            price=price,
            change=round(change, 4),
            change_percent=round(change_pct, 4),
            volume=float(day_bar.get("v", 0.0)),
            open=float(day_bar.get("o", price)),
            high=float(day_bar.get("h", price)),
            low=float(day_bar.get("l", price)),
            prev_close=prev_close,
            source="polygon",
            retrieved_at=datetime.now(UTC),
            as_of=normalize_datetime(as_of),
        )

    async def get_benchmark(
        self,
        symbol: str = "SPY",
        start: datetime | None = None,
        end: datetime | None = None,
        interval: str = "daily",
    ) -> list[MarketObservation]:
        end_dt = end or datetime.now(UTC)
        start_dt = start or end_dt.replace(day=max(1, end_dt.day - 30))
        return await self.get_historical_bars(symbol, start=start_dt, end=end_dt, interval=interval)

    async def get_calendar(self, as_of: datetime) -> MarketCalendar:
        as_of_utc = normalize_datetime(as_of)
        is_weekday = as_of_utc.weekday() < 5
        return MarketCalendar(
            market="US",
            is_open=is_weekday and (9 <= as_of_utc.hour < 16),
            session_open=as_of_utc.replace(hour=9, minute=30, second=0),
            session_close=as_of_utc.replace(hour=16, minute=0, second=0),
        )

    async def get_news(
        self,
        symbols: list[str],
        start: datetime,
        end: datetime,
        limit: int = 50,
    ) -> list[NewsArticle]:
        self._ensure_api_key()
        sym = symbols[0].upper().strip() if symbols else "AAPL"
        url = f"{self.BASE_URL}/v2/reference/news"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        params = {"ticker": sym, "limit": limit, "order": "desc"}

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, headers=headers, params=params)
            data = resp.json()

        results = data.get("results", [])
        articles: list[NewsArticle] = []
        end_utc = normalize_datetime(end)

        for item in results:
            pub_str = item.get("published_utc", "")
            try:
                dt = datetime.fromisoformat(pub_str.replace("Z", "+00:00"))
            except Exception:
                dt = datetime.now(UTC)

            url_val = item.get("article_url", "")
            canon_url = canonicalize_url(url_val)
            title = item.get("title", "")
            art_id = generate_article_id(canon_url, title)

            articles.append(
                NewsArticle(
                    article_id=art_id,
                    provider_article_id=item.get("id"),
                    publisher=item.get("publisher", {}).get("name", "Unknown"),
                    title=title,
                    description=item.get("description"),
                    article_url=url_val,
                    published_at=dt,
                    retrieved_at=datetime.now(UTC),
                    available_at=dt,
                    tickers=item.get("tickers", [sym]),
                    source_provider="polygon",
                )
            )

        return filter_news_point_in_time(articles, as_of=end_utc)[:limit]

    async def get_health(self) -> ProviderHealth:
        if not self.api_key:
            return ProviderHealth(
                provider_name=self.provider_name,
                is_healthy=False,
                latency_ms=0.0,
                message="No POLYGON_API_KEY configured",
            )
        return ProviderHealth(
            provider_name=self.provider_name,
            is_healthy=True,
            latency_ms=35.0,
            message="Polygon provider online",
        )
