"""Market Data Agent implementation."""

from datetime import timedelta

from services.finance_mcp.server import FinanceMCPServer
from src.agents.base import BaseAgent, MarketDataAgentOutput
from src.contracts.analysis import AnalysisRequest
from src.contracts.mcp import AgentRole, WorkflowState
from src.observability.logging import get_logger

logger = get_logger("market_data_agent")


class MarketDataAgent(BaseAgent):
    """Specialist agent responsible for market data and news acquisition."""

    def __init__(self, mcp_server: FinanceMCPServer):
        super().__init__(mcp_server, role=AgentRole.MARKET_DATA)

    async def run(self, request: AnalysisRequest) -> MarketDataAgentOutput:
        context = self.create_context(
            run_id=request.run_id,
            analysis_timestamp=request.analysis_timestamp,
            workflow_state=WorkflowState.DATA_COLLECTION,
        )

        market_artifacts: list[str] = []
        news_artifacts: list[str] = []
        freshness_dict: dict[str, float] = {}
        warnings: list[str] = []

        # 1. Check Calendar
        cal = await self.call_tool("fetch_market_calendar", {}, context)
        session_status = {"US": "OPEN" if cal.get("is_open") else "CLOSED"}

        # 2. Acquire data for each symbol
        for symbol in request.symbols:
            # Resolve symbol
            try:
                await self.call_tool("resolve_symbol", {"symbol": symbol}, context)
            except Exception as e:
                warnings.append(f"Failed to resolve symbol {symbol}: {e!s}")
                continue

            # Fetch snapshot quote
            try:
                snap = await self.call_tool("fetch_market_snapshot", {"symbol": symbol}, context)
                freshness_dict[symbol] = snap.get("freshness_seconds", 0.0)
                if snap.get("is_stale"):
                    warnings.append(
                        f"Market snapshot for {symbol} is stale ({snap.get('freshness_seconds', 0) / 60:.1f}m old)"
                    )
                market_artifacts.append(f"artifact://{request.run_id}/market_snapshot/{symbol}")
            except Exception as e:
                warnings.append(f"Failed fetching snapshot for {symbol}: {e!s}")

            # Fetch historical bars
            start_date = request.analysis_timestamp - timedelta(days=request.price_lookback_days)
            try:
                await self.call_tool(
                    "fetch_historical_bars",
                    {
                        "symbol": symbol,
                        "start": start_date,
                        "end": request.analysis_timestamp,
                        "interval": "daily",
                    },
                    context,
                )
                market_artifacts.append(f"artifact://{request.run_id}/raw_market/{symbol}")
            except Exception as e:
                warnings.append(f"Failed fetching bars for {symbol}: {e!s}")

        # 3. Benchmark
        try:
            await self.call_tool("fetch_market_benchmark", {"symbol": "SPY"}, context)
            market_artifacts.append(f"artifact://{request.run_id}/benchmark/SPY")
        except Exception as e:
            warnings.append(f"Benchmark SPY retrieval failed: {e!s}")

        # 4. News
        try:
            await self.call_tool(
                "fetch_market_news",
                {
                    "symbols": request.symbols,
                    "lookback_hours": request.news_lookback_hours,
                    "limit": 50,
                },
                context,
            )
            news_artifacts.append(f"artifact://{request.run_id}/raw_news/all")
        except Exception as e:
            warnings.append(f"News retrieval failed: {e!s}")

        status = "degraded" if warnings else "complete"
        return MarketDataAgentOutput(
            status=status,
            market_artifacts=market_artifacts,
            news_artifacts=news_artifacts,
            freshness=freshness_dict,
            session_status=session_status,
            warnings=warnings,
        )
