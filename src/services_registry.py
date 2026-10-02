"""Services registry providing dependency injection for MCP, agents, and orchestrator."""

from dataclasses import dataclass

from src.providers.base import BaseMarketDataProvider, BaseNewsProvider
from src.providers.fixture_provider import FixtureMarketDataProvider, FixtureNewsProvider
from src.storage.artifacts import ArtifactStorage
from src.storage.lineage import LineageTracker
from src.storage.repository import ResearchRepository


@dataclass
class AppServices:
    market_provider: BaseMarketDataProvider
    news_provider: BaseNewsProvider
    storage: ArtifactStorage
    repo: ResearchRepository
    lineage: LineageTracker


def create_default_services(mode: str = "fixture") -> AppServices:
    """Factory creating configured services for fixture or live mode."""
    storage = ArtifactStorage()
    repo = ResearchRepository()
    lineage = LineageTracker()

    if mode == "fixture":
        market_provider = FixtureMarketDataProvider()
        news_provider = FixtureNewsProvider()
    else:
        from src.providers.alphavantage import AlphaVantageProvider

        market_provider = AlphaVantageProvider()
        news_provider = AlphaVantageProvider()

    return AppServices(
        market_provider=market_provider,
        news_provider=news_provider,
        storage=storage,
        repo=repo,
        lineage=lineage,
    )
