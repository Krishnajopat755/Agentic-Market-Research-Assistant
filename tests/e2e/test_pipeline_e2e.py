"""End-to-end integration and pipeline verification tests."""

from datetime import UTC, datetime

import pytest

from src.contracts.analysis import AnalysisRequest
from src.contracts.errors import ErrorCode
from src.orchestration.workflow import ResearchOrchestrator
from src.providers.fixture_provider import FixtureMarketDataProvider, FixtureNewsProvider
from src.services_registry import AppServices, create_default_services
from src.storage.artifacts import ArtifactStorage
from src.storage.lineage import LineageTracker
from src.storage.repository import ResearchRepository


@pytest.mark.asyncio
async def test_full_pipeline_aapl():
    services = create_default_services(mode="fixture")
    orchestrator = ResearchOrchestrator(services)

    req = AnalysisRequest(
        symbols=["AAPL"],
        analysis_timestamp=datetime(2026, 9, 25, 16, 10, tzinfo=UTC),
        price_lookback_days=120,
        news_lookback_hours=24,
    )

    ctx = await orchestrator.execute_run(req)

    assert ctx.state.value == "COMPLETED"
    sym_state = ctx.symbols_data["AAPL"]
    assert sym_state.snapshot is not None
    assert sym_state.snapshot.price > 0
    assert sym_state.technical is not None
    assert sym_state.technical.rsi_14 is not None
    assert sym_state.signal is not None
    assert sym_state.signal.state in ("BULLISH", "NEUTRAL", "BEARISH")
    assert sym_state.report is not None
    assert "Apple" in sym_state.report.headline or "AAPL" in sym_state.report.headline
    assert len(sym_state.report.evidence) > 0


@pytest.mark.asyncio
async def test_multi_symbol_watchlist():
    services = create_default_services(mode="fixture")
    orchestrator = ResearchOrchestrator(services)

    req = AnalysisRequest(
        symbols=["AAPL", "MSFT"],
        analysis_timestamp=datetime(2026, 9, 25, 16, 10, tzinfo=UTC),
    )

    ctx = await orchestrator.execute_run(req)
    assert ctx.state.value == "COMPLETED"
    assert "AAPL" in ctx.symbols_data
    assert "MSFT" in ctx.symbols_data
    assert ctx.symbols_data["AAPL"].report is not None
    assert ctx.symbols_data["MSFT"].report is not None


@pytest.mark.asyncio
async def test_provider_transient_failure_recovery():
    """Verify that orchestrator recovers from transient rate limit failures with backoff."""
    # Inject a 1-time rate limit error into the fixture provider
    market_provider = FixtureMarketDataProvider(
        simulate_failure_code=ErrorCode.RATE_LIMITED,
        simulate_failure_count=1,
    )
    news_provider = FixtureNewsProvider()

    services = AppServices(
        market_provider=market_provider,
        news_provider=news_provider,
        storage=ArtifactStorage(),
        repo=ResearchRepository(),
        lineage=LineageTracker(),
    )

    orchestrator = ResearchOrchestrator(services, max_retries=3, retry_backoff_base=0.1)

    req = AnalysisRequest(
        symbols=["AAPL"],
        analysis_timestamp=datetime(2026, 9, 25, 16, 10, tzinfo=UTC),
    )

    ctx = await orchestrator.execute_run(req)
    assert ctx.state.value == "COMPLETED"
    assert ctx.symbols_data["AAPL"].report is not None
