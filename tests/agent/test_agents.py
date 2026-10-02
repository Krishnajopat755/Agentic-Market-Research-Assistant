"""Unit and interaction tests for runtime agents."""

from datetime import UTC, datetime

import pytest

from services.finance_mcp.server import FinanceMCPServer
from src.agents.market_data import MarketDataAgent
from src.contracts.analysis import AnalysisRequest
from src.services_registry import create_default_services


@pytest.fixture
def agent_setup():
    services = create_default_services(mode="fixture")
    server = FinanceMCPServer(services)
    return services, server


@pytest.mark.asyncio
async def test_market_data_agent(agent_setup):
    services, server = agent_setup
    agent = MarketDataAgent(server)
    req = AnalysisRequest(
        symbols=["AAPL"],
        analysis_timestamp=datetime(2026, 9, 25, 16, 10, tzinfo=UTC),
    )

    out = await agent.run(req)
    assert out.status in ("complete", "degraded")
    assert len(out.market_artifacts) > 0
    assert len(out.news_artifacts) > 0
    assert "AAPL" in out.freshness
