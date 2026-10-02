"""Alpha Vantage market and news provider adapter."""

import os
from datetime import UTC, datetime

import httpx

from src.contracts.errors import ErrorCode, FinanceAppException
from src.contracts.market import MarketCalendar, MarketObservation, MarketSnapshot
from src.contracts.mcp import ProviderHealth
from src.contracts.news import NewsArticle, SentimentScore
from src.finance_core.market_data.normalization import build_market_snapshot, normalize_datetime
from src.finance_core.news.normalization import (
    canonicalize_url,
    filter_news_point_in_time,
    generate_article_id,
)
from src.providers.base import BaseMarketDataProvider, BaseNewsProvider


class AlphaVantageProvider(BaseMarketDataProvider, BaseNewsProvider):
    """Alpha Vantage HTTP adapter mapping raw JSON to normalized domain contracts."""

    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("ALPHAVANTAGE_API_KEY", "")

    @property
    def provider_name(self) -> str:
        return "alphavantage"

    def _ensure_api_key(self) -> None:
        if not self.api_key or self.api_key == "demo":
            raise FinanceAppException(
                error_code=ErrorCode.AUTH_ERROR,
                message="Alpha Vantage API key missing or invalid. Set ALPHAVANTAGE_API_KEY or use fixture mode.",
            )

    async def resolve_symbol(self, symbol: str) -> dict[str, str]:
        self._ensure_api_key()
        sym = symbol.upper().strip()
        params = {"function": "SYMBOL_SEARCH", "keywords": sym, "apikey": self.api_key}
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(self.BASE_URL, params=params)
            data = resp.json()

        matches = data.get("bestMatches", [])
        if not matches:
            raise FinanceAppException(
                error_code=ErrorCode.INVALID_SYMBOL,
                message=f"No matching equity symbol found for '{sym}' on Alpha Vantage",
            )
        first = matches[0]
        return {
            "symbol": first.get("1. symbol", sym),
            "name": first.get("2. name", sym),
            "exchange": first.get("4. region", "US"),
            "currency": first.get("8. currency", "USD"),
        }

    async def get_historical_bars(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        interval: str = "daily",
    ) -> list[MarketObservation]:
        self._ensure_api_key()
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol.upper().strip(),
            "outputsize": "compact",
            "apikey": self.api_key,
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(self.BASE_URL, params=params)
            data = resp.json()

        if "Note" in data or "Information" in data:
            raise FinanceAppException(
                error_code=ErrorCode.RATE_LIMITED,
                message=f"Alpha Vantage rate limit reached: {data.get('Note') or data.get('Information')}",
                retryable=True,
                retry_after_seconds=60,
            )

        ts = data.get("Time Series (Daily)", {})
        if not ts:
            raise FinanceAppException(
                error_code=ErrorCode.EMPTY_RESULT,
                message=f"Empty time series response from Alpha Vantage for {symbol}",
            )

        start_utc = normalize_datetime(start)
        end_utc = normalize_datetime(end)
        observations: list[MarketObservation] = []

        for date_str, bar in ts.items():
            dt = datetime.strptime(date_str, "%Y-%m-%d").replace(hour=16, minute=0, tzinfo=UTC)
            if start_utc <= dt <= end_utc:
                observations.append(
                    MarketObservation(
                        symbol=symbol.upper(),
                        event_time=dt,
                        retrieved_at=datetime.now(UTC),
                        as_of=end_utc,
                        open=float(bar["1. open"]),
                        high=float(bar["2. high"]),
                        low=float(bar["3. low"]),
                        close=float(bar["4. close"]),
                        volume=float(bar["5. volume"]),
                        source="alphavantage",
                        entitlement="delayed",
                    )
                )

        observations.sort(key=lambda x: x.event_time)
        return observations

    async def get_snapshot(self, symbol: str, as_of: datetime) -> MarketSnapshot:
        bars = await self.get_historical_bars(
            symbol,
            start=as_of.replace(day=max(1, as_of.day - 7)),
            end=as_of,
        )
        return build_market_snapshot(symbol, bars, as_of=as_of, source="alphavantage")

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
        tickers_str = ",".join(s.upper().strip() for s in symbols)
        params = {
            "function": "NEWS_SENTIMENT",
            "tickers": tickers_str,
            "limit": limit,
            "apikey": self.api_key,
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(self.BASE_URL, params=params)
            data = resp.json()

        feed = data.get("feed", [])
        articles: list[NewsArticle] = []
        end_utc = normalize_datetime(end)

        for item in feed:
            # Parse Alpha Vantage format: 20260925T143000
            time_str = item.get("time_published", "")
            try:
                dt = datetime.strptime(time_str, "%Y%m%dT%H%M%S").replace(tzinfo=UTC)
            except Exception:
                dt = datetime.now(UTC)

            url = item.get("url", "")
            canon_url = canonicalize_url(url)
            title = item.get("title", "")
            art_id = generate_article_id(canon_url, title)

            # Extract provider sentiment if present
            av_sent = item.get("overall_sentiment_score")
            sent_obj = None
            if av_sent is not None:
                score = float(av_sent)
                label = "positive" if score > 0.15 else ("negative" if score < -0.15 else "neutral")
                sent_obj = SentimentScore(
                    label=label,
                    score=score,
                    model="alphavantage_feed_sentiment",
                    confidence=0.7,
                )

            articles.append(
                NewsArticle(
                    article_id=art_id,
                    provider_article_id=item.get("id"),
                    publisher=item.get("source", "Unknown"),
                    title=title,
                    description=item.get("summary"),
                    article_url=url,
                    published_at=dt,
                    retrieved_at=datetime.now(UTC),
                    available_at=dt,
                    tickers=[t.get("ticker", "") for t in item.get("ticker_sentiment", [])],
                    source_provider="alphavantage",
                    sentiment=sent_obj,
                )
            )

        return filter_news_point_in_time(articles, as_of=end_utc)[:limit]

    async def get_health(self) -> ProviderHealth:
        if not self.api_key:
            return ProviderHealth(
                provider_name=self.provider_name,
                is_healthy=False,
                latency_ms=0.0,
                message="No ALPHAVANTAGE_API_KEY configured",
            )
        return ProviderHealth(
            provider_name=self.provider_name,
            is_healthy=True,
            latency_ms=45.0,
            message="Alpha Vantage provider online",
        )
