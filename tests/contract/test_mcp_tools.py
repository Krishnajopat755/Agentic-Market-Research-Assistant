"""Contract tests for Finance MCP Server tools and role authorization."""

from datetime import UTC, datetime

import pytest

from services.finance_mcp.server import FinanceMCPServer
from src.contracts.errors import ErrorCode
from src.contracts.mcp import AgentRole, ToolContext, WorkflowState
from src.services_registry import create_default_services


@pytest.fixture
def mcp_server():
    services = create_default_services(mode="fixture")
    return FinanceMCPServer(services)


@pytest.mark.asyncio
async def test_mcp_tool_catalog(mcp_server):
    tools = mcp_server.list_tools()
    assert "resolve_symbol" in tools
    assert "fetch_market_snapshot" in tools
    assert "fetch_market_news" in tools
    assert "compute_technical_indicators" in tools
    assert "run_signal_model" in tools
    assert "render_daily_report" in tools
    assert len(tools) == 20


@pytest.mark.asyncio
async def test_synthesis_agent_forbidden_from_news_retrieval(mcp_server):
    """Critical Acceptance Test: Synthesis Agent cannot call raw news retrieval tools."""
    context = ToolContext(
        run_id="test-run-001",
        analysis_timestamp=datetime(2026, 9, 25, 16, 10, tzinfo=UTC),
        caller_role=AgentRole.SYNTHESIS_REPORT,
        workflow_state=WorkflowState.SYNTHESIS,
    )

    res = await mcp_server.execute_tool("fetch_market_news", {"symbols": ["AAPL"]}, context)
    assert res["status"] == "error"
    assert res["error"]["error_code"] == ErrorCode.TOOL_NOT_AUTHORIZED.value


@pytest.mark.asyncio
async def test_market_agent_forbidden_from_signal_generation(mcp_server):
    """Market Data Agent cannot call final signal generation."""
    context = ToolContext(
        run_id="test-run-002",
        analysis_timestamp=datetime(2026, 9, 25, 16, 10, tzinfo=UTC),
        caller_role=AgentRole.MARKET_DATA,
        workflow_state=WorkflowState.DATA_COLLECTION,
    )

    res = await mcp_server.execute_tool("run_signal_model", {"features": {}}, context)
    assert res["status"] == "error"
    assert res["error"]["error_code"] == ErrorCode.TOOL_NOT_AUTHORIZED.value


@pytest.mark.asyncio
async def test_authorized_market_snapshot(mcp_server):
    context = ToolContext(
        run_id="test-run-003",
        analysis_timestamp=datetime(2026, 9, 25, 16, 10, tzinfo=UTC),
        caller_role=AgentRole.MARKET_DATA,
        workflow_state=WorkflowState.DATA_COLLECTION,
    )

    res = await mcp_server.execute_tool("fetch_market_snapshot", {"symbol": "AAPL"}, context)
    assert res["status"] == "success"
    assert res["result"]["symbol"] == "AAPL"
    assert res["result"]["price"] > 0
