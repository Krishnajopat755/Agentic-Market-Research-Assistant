# Market Data Provider Specification

## 1. Provider strategy

Use provider adapters. The domain layer must not assume a specific vendor's quotas, real-time access, exchange coverage, or response schema.

## 2. Alpha Vantage

The current Alpha Vantage documentation exposes daily equity time series, news & sentiment, and technical-indicator APIs. Some endpoints/data entitlements depend on the account/plan.

Use Alpha Vantage as a practical initial adapter, not as a hard-coded domain dependency.

Reference:
https://www.alphavantage.co/documentation/

## 3. Polygon/Massive

Polygon's current stock APIs include news and ticker snapshot endpoints with publication timestamps and market snapshot metadata where supported by the endpoint/account.

References:
https://polygon.io/docs/rest/stocks/news
https://polygon.io/docs/rest/stocks/snapshots/single-ticker-snapshot

## 4. Provider interfaces

```python
class MarketDataProvider(Protocol):
    async def resolve_symbol(self, symbol: str) -> SymbolRef: ...
    async def snapshot(self, symbol: str, as_of: datetime) -> MarketSnapshot: ...
    async def historical_bars(
        self, symbol: str, start: datetime, end: datetime, interval: str
    ) -> list[MarketBar]: ...
    async def benchmark(
        self, symbol: str, start: datetime, end: datetime, interval: str
    ) -> list[MarketBar]: ...
    async def calendar(self, start: date, end: date) -> list[MarketSession]: ...


class NewsProvider(Protocol):
    async def news(
        self, symbols: list[str], start: datetime, end: datetime
    ) -> list[NewsArticle]: ...
```

## 5. Caching

Cache:
- symbol metadata;
- historical bars;
- news responses;
- provider capabilities.

Latest mutable observations use a short configurable TTL.

## 6. Pagination

Adapters must:
- follow provider pagination safely;
- cap pages;
- preserve request IDs;
- stop at analysis cutoff;
- record the page count.

## 7. Rate limits

Implement:
- Retry-After handling;
- exponential backoff;
- bounded retries;
- concurrency limits;
- cache where allowed.

## 8. Source attribution

Keep publisher/provider, URL, publication time, and retrieval time. Provider-provided sentiment must be labeled as provider sentiment rather than model-generated sentiment.
