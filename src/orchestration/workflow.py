"""Orchestrator state machine coordinating multi-agent research workflow."""

import asyncio
from datetime import UTC, datetime, timedelta

from services.finance_mcp.server import FinanceMCPServer
from src.agents.market_data import MarketDataAgent
from src.agents.sentiment_technical import SentimentTechnicalAgent
from src.agents.synthesis_report import SynthesisReportAgent
from src.contracts.analysis import AnalysisRequest
from src.contracts.errors import FinanceAppException
from src.contracts.market import MarketObservation, MarketSnapshot
from src.contracts.mcp import AgentRole, ToolContext, WorkflowState
from src.contracts.news import AggregateSentiment, NewsArticle
from src.contracts.technical import TechnicalSnapshot
from src.llm.base import BaseLLMAdapter
from src.observability.logging import get_logger
from src.observability.tracing import default_tracer
from src.orchestration.state import ResearchRunContext, SymbolWorkflowState
from src.services_registry import AppServices

logger = get_logger("orchestrator")


class ResearchOrchestrator:
    """Multi-agent orchestrator managing state transitions, retries, and artifacts."""

    def __init__(
        self,
        services: AppServices,
        llm_adapter: BaseLLMAdapter | None = None,
        max_retries: int = 3,
        retry_backoff_base: float = 0.5,
    ):
        self.services = services
        self.mcp_server = FinanceMCPServer(services)
        self.max_retries = max_retries
        self.retry_backoff_base = retry_backoff_base

        # Initialize specialist agents
        self.market_agent = MarketDataAgent(self.mcp_server)
        self.analytics_agent = SentimentTechnicalAgent(self.mcp_server)
        self.synthesis_agent = SynthesisReportAgent(self.mcp_server, llm_adapter=llm_adapter)

    async def execute_run(self, request: AnalysisRequest) -> ResearchRunContext:
        """Execute the end-to-end multi-agent research workflow."""
        with default_tracer.start_span("orchestrator.run", attributes={"run_id": request.run_id}):
            # Create repository run record
            self.services.repo.create_run(request)

            ctx = ResearchRunContext(
                run_id=request.run_id,
                request=request,
                state=WorkflowState.INITIALIZED,
            )
            for sym in request.symbols:
                ctx.symbols_data[sym] = SymbolWorkflowState(symbol=sym)

            try:
                # -------------------------------------------------------------
                # Phase 1: Data Collection
                # -------------------------------------------------------------
                ctx.state = WorkflowState.DATA_COLLECTION
                self.services.repo.update_state(request.run_id, ctx.state)
                await self._retry_step(lambda: self._step_data_collection(ctx))

                # -------------------------------------------------------------
                # Phase 2: Analytics & Feature Processing
                # -------------------------------------------------------------
                ctx.state = WorkflowState.ANALYTICS_PROCESSING
                self.services.repo.update_state(request.run_id, ctx.state)
                await self._retry_step(lambda: self._step_analytics(ctx))

                # -------------------------------------------------------------
                # Phase 3: Synthesis & Reporting
                # -------------------------------------------------------------
                ctx.state = WorkflowState.SYNTHESIS
                self.services.repo.update_state(request.run_id, ctx.state)
                await self._retry_step(lambda: self._step_synthesis(ctx))

                ctx.state = WorkflowState.COMPLETED
                ctx.completed_at = datetime.now(UTC)
                self.services.repo.update_state(request.run_id, ctx.state)

                # Persist run lineage
                self._record_lineage(ctx)
                logger.info(f"Research run {request.run_id} completed successfully.")

            except Exception as e:
                ctx.state = WorkflowState.FAILED
                ctx.errors.append(str(e))
                self.services.repo.update_state(request.run_id, ctx.state)
                logger.error(f"Research run {request.run_id} failed: {e!s}")
                raise

            return ctx

    async def _retry_step(self, step_fn):
        """Execute step with exponential backoff on transient errors."""
        last_ex = None
        for attempt in range(1, self.max_retries + 1):
            try:
                return await step_fn()
            except FinanceAppException as fe:
                last_ex = fe
                if not fe.envelope.retryable or attempt == self.max_retries:
                    raise
                backoff = fe.envelope.retry_after_seconds or (
                    self.retry_backoff_base * (2 ** (attempt - 1))
                )
                logger.warning(
                    f"Transient error on attempt {attempt}: {fe.envelope.message}. Retrying in {backoff}s..."
                )
                await asyncio.sleep(backoff)
            except Exception as e:
                last_ex = e
                if attempt == self.max_retries:
                    raise
                await asyncio.sleep(self.retry_backoff_base * (2 ** (attempt - 1)))
        raise last_ex

    async def _step_data_collection(self, ctx: ResearchRunContext) -> None:
        """Run Market Data Agent and populate intermediate context."""
        agent_out = await self.market_agent.run(ctx.request)
        ctx.warnings.extend(agent_out.warnings)

        # Retrieve observations and news from MCP tools to populate symbol states
        orch_context = ToolContext(
            run_id=ctx.run_id,
            analysis_timestamp=ctx.request.analysis_timestamp,
            caller_role=AgentRole.ORCHESTRATOR,
            workflow_state=ctx.state,
        )

        # Benchmark
        bench = await self.mcp_server.execute_tool(
            "fetch_market_benchmark", {"symbol": "SPY"}, orch_context
        )
        if bench.get("status") == "success":
            ctx.benchmark_bars = [MarketObservation(**b) for b in bench["result"]]

        # News
        news_res = await self.mcp_server.execute_tool(
            "fetch_market_news",
            {"symbols": ctx.request.symbols, "lookback_hours": ctx.request.news_lookback_hours},
            orch_context,
        )
        all_news = (
            [NewsArticle(**n) for n in news_res.get("result", [])]
            if news_res.get("status") == "success"
            else []
        )

        # Populate each symbol
        for symbol, sym_state in ctx.symbols_data.items():
            # Snapshot
            snap_res = await self.mcp_server.execute_tool(
                "fetch_market_snapshot", {"symbol": symbol}, orch_context
            )
            if snap_res.get("status") == "success":
                sym_state.snapshot = MarketSnapshot(**snap_res["result"])

            # Historical bars
            bars_res = await self.mcp_server.execute_tool(
                "fetch_historical_bars",
                {
                    "symbol": symbol,
                    "start": ctx.request.analysis_timestamp
                    - timedelta(days=ctx.request.price_lookback_days),
                    "end": ctx.request.analysis_timestamp,
                },
                orch_context,
            )
            if bars_res.get("status") == "success":
                sym_state.bars = [MarketObservation(**b) for b in bars_res["result"]]

            # News tagged with symbol
            sym_state.news = [
                art
                for art in all_news
                if not art.tickers or symbol.upper() in [t.upper() for t in art.tickers]
            ]

    async def _step_analytics(self, ctx: ResearchRunContext) -> None:
        """Run Sentiment & Technical Agent across watchlist."""
        for symbol, sym_state in ctx.symbols_data.items():
            if not sym_state.bars:
                sym_state.errors.append("No market bars available for analytics")
                continue

            out = await self.analytics_agent.run(
                request=ctx.request,
                symbol=symbol,
                observations=sym_state.bars,
                news_articles=sym_state.news,
                benchmark=ctx.benchmark_bars,
            )
            sym_state.signal = out.signal_candidate

            # Load technical & sentiment from storage
            orch_context = ToolContext(
                run_id=ctx.run_id,
                analysis_timestamp=ctx.request.analysis_timestamp,
                caller_role=AgentRole.ORCHESTRATOR,
                workflow_state=ctx.state,
            )
            tech_res = await self.mcp_server.execute_tool(
                "compute_technical_indicators",
                {"symbol": symbol, "observations": sym_state.bars},
                orch_context,
            )
            if tech_res.get("status") == "success":
                sym_state.technical = TechnicalSnapshot(**tech_res["result"])

            sent_res = await self.mcp_server.execute_tool(
                "aggregate_news_sentiment",
                {"symbol": symbol, "articles": sym_state.news},
                orch_context,
            )
            if sent_res.get("status") == "success":
                sym_state.sentiment = AggregateSentiment(**sent_res["result"])

    async def _step_synthesis(self, ctx: ResearchRunContext) -> None:
        """Run Synthesis & Report Agent across watchlist."""
        for symbol, sym_state in ctx.symbols_data.items():
            if not sym_state.snapshot or not sym_state.technical or not sym_state.signal:
                continue

            await self.synthesis_agent.run(
                request=ctx.request,
                symbol=symbol,
                snapshot=sym_state.snapshot,
                technical=sym_state.technical,
                sentiment=sym_state.sentiment
                or AggregateSentiment(symbol=symbol, as_of=ctx.request.analysis_timestamp),
                signal=sym_state.signal,
                top_news=sym_state.news,
            )
            # Retrieve generated DailyResearchReport from repository
            run = self.services.repo.get_run(ctx.run_id)
            if run and symbol in run.reports:
                sym_state.report = run.reports[symbol]

    def _record_lineage(self, ctx: ResearchRunContext) -> None:
        """Log MLflow-compatible lineage metadata."""
        params = {
            "symbols": ctx.request.symbols,
            "lookback_days": ctx.request.price_lookback_days,
            "horizon_bars": ctx.request.signal_horizon_bars,
            "analysis_timestamp": ctx.request.analysis_timestamp.isoformat(),
        }
        metrics = {}
        for sym, s_data in ctx.symbols_data.items():
            if s_data.signal:
                metrics[f"{sym}_signal_score"] = s_data.signal.score
                metrics[f"{sym}_confidence"] = s_data.signal.confidence
            if s_data.technical and s_data.technical.returns_5d is not None:
                metrics[f"{sym}_returns_5d"] = s_data.technical.returns_5d

        tags = {
            "mode": "fixture" if isinstance(self.services.market_provider, object) else "live",
            "status": ctx.state.value,
        }
        self.services.lineage.log_run_lineage(
            run_id=ctx.run_id,
            parameters=params,
            metrics=metrics,
            tags=tags,
            model_version="scorecard-v1.0.0",
        )
