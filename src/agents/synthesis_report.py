"""Synthesis & Report Agent implementation."""

from services.finance_mcp.server import FinanceMCPServer
from src.agents.base import BaseAgent, SynthesisReportAgentOutput
from src.contracts.analysis import AnalysisRequest
from src.contracts.evidence import ResearchEvidence
from src.contracts.market import MarketSnapshot
from src.contracts.mcp import AgentRole, WorkflowState
from src.contracts.news import AggregateSentiment, NewsArticle
from src.contracts.report import DailyResearchReport
from src.contracts.signal import SignalResult
from src.contracts.technical import TechnicalSnapshot
from src.llm.base import BaseLLMAdapter, LLMMessage
from src.observability.logging import get_logger

logger = get_logger("synthesis_report_agent")


class SynthesisReportAgent(BaseAgent):
    """Specialist agent responsible for research synthesis, claim validation, and report creation."""

    def __init__(self, mcp_server: FinanceMCPServer, llm_adapter: BaseLLMAdapter | None = None):
        super().__init__(mcp_server, role=AgentRole.SYNTHESIS_REPORT)
        if llm_adapter is None:
            from src.llm.mock_adapter import MockLLMAdapter

            llm_adapter = MockLLMAdapter()
        self.llm = llm_adapter

    async def run(
        self,
        request: AnalysisRequest,
        symbol: str,
        snapshot: MarketSnapshot,
        technical: TechnicalSnapshot,
        sentiment: AggregateSentiment,
        signal: SignalResult,
        top_news: list[NewsArticle],
    ) -> SynthesisReportAgentOutput:
        context = self.create_context(
            run_id=request.run_id,
            analysis_timestamp=request.analysis_timestamp,
            workflow_state=WorkflowState.SYNTHESIS,
        )

        # 1. Fetch available evidence
        evidence_pool_raw = await self.call_tool(
            "get_research_evidence", {"symbol": symbol}, context
        )
        evidence_pool = [ResearchEvidence(**e) for e in evidence_pool_raw]

        # 2. Synthesize narrative via LLM adapter
        from src.providers.indian_stocks import get_equity_metadata

        meta = get_equity_metadata(symbol)
        curr = meta.get("currency_symbol", "₹" if symbol.endswith((".NS", ".BO")) else "$")

        ret_5d_str = f"{technical.returns_5d:+.2%}" if technical.returns_5d is not None else "0%"
        prompt = (
            f"Analyze research findings for {symbol} as of {request.analysis_timestamp.isoformat()}.\n"
            f"Company: {meta['name']} ({meta['sector']})\n"
            f"Market State: {signal.state} (Score: {signal.score:+.2f}, Confidence: {signal.confidence:.1%})\n"
            f"Latest Price: {curr}{snapshot.price:.2f}, 5d Return: {ret_5d_str}\n"
            f"RSI: {technical.rsi_14 or 'N/A'}, SMA20: {technical.sma_20 or 'N/A'}\n"
            f"Mean Sentiment: {sentiment.mean_score:+.2f} over {sentiment.article_count} articles.\n"
            "Create structured synthesis. Every claim must refer to verifiable evidence."
        )

        llm_resp = await self.llm.complete(
            messages=[
                LLMMessage(
                    role="system",
                    content="You are the Synthesis & Report Agent. Ground all claims in provided evidence.",
                ),
                LLMMessage(role="user", content=prompt),
            ],
            response_schema=SynthesisReportAgentOutput,
            trace_context={"run_id": request.run_id, "symbol": symbol},
        )

        output: SynthesisReportAgentOutput
        if llm_resp.structured_output:
            output = SynthesisReportAgentOutput(**llm_resp.structured_output)
        else:
            output = SynthesisReportAgentOutput(
                headline=f"{meta['name']} Market Research Synthesis",
                market_state=signal.state,
                signal_score=signal.score,
                confidence=signal.confidence,
                executive_summary=f"{symbol} ({meta['name']}) shows a {signal.state} posture with quantitative score {signal.score:+.2f}.",
                key_evidence=evidence_pool[:3],
                caveats=signal.limitations,
            )

        # 3. Validate claims through MCP tool
        await self.call_tool(
            "validate_report_claims",
            {"claims": output.key_evidence},
            context,
        )

        # 4. Construct complete DailyResearchReport
        scenario_analysis = {
            "bull_case": f"Momentum continues above {curr}{snapshot.price * 1.05:.2f} driven by sustained institutional accumulation.",
            "base_case": f"Consolidation near {curr}{snapshot.price:.2f} within 20-day volatility band.",
            "bear_case": f"Breakdown below support at {curr}{snapshot.price * 0.95:.2f} if sentiment deteriorates.",
        }

        report = DailyResearchReport(
            run_id=request.run_id,
            symbol=symbol,
            analysis_timestamp=request.analysis_timestamp,
            timezone=request.timezone,
            market_state=output.market_state,
            signal_score=output.signal_score,
            confidence=output.confidence,
            headline=output.headline,
            executive_summary=output.executive_summary,
            snapshot=snapshot,
            technical=technical,
            sentiment=sentiment,
            top_news=top_news[:5],
            signal=signal,
            evidence=output.key_evidence,
            scenario_analysis=scenario_analysis,
            known_limitations=signal.limitations,
            freshness_warnings=["Snapshot is stale"] if snapshot.is_stale else [],
        )

        # 5. Persist research record
        save_res = await self.call_tool(
            "persist_research_record",
            {"report": report},
            context,
        )
        output.report_ref = save_res.get("artifact_ref")

        return output
