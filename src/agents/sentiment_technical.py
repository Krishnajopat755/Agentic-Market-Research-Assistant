"""Sentiment & Technical Analysis Agent implementation."""

from services.finance_mcp.server import FinanceMCPServer
from src.agents.base import BaseAgent, SentimentTechnicalAgentOutput
from src.contracts.analysis import AnalysisRequest
from src.contracts.features import ResearchFeatures
from src.contracts.market import MarketObservation
from src.contracts.mcp import AgentRole, WorkflowState
from src.contracts.news import AggregateSentiment, NewsArticle
from src.contracts.signal import SignalResult
from src.contracts.technical import TechnicalSnapshot
from src.observability.logging import get_logger

logger = get_logger("sentiment_technical_agent")


class SentimentTechnicalAgent(BaseAgent):
    """Specialist agent responsible for deterministic technical and sentiment analytics."""

    def __init__(self, mcp_server: FinanceMCPServer):
        super().__init__(mcp_server, role=AgentRole.SENTIMENT_TECHNICAL)

    async def run(
        self,
        request: AnalysisRequest,
        symbol: str,
        observations: list[MarketObservation],
        news_articles: list[NewsArticle],
        benchmark: list[MarketObservation] | None = None,
    ) -> SentimentTechnicalAgentOutput:
        context = self.create_context(
            run_id=request.run_id,
            analysis_timestamp=request.analysis_timestamp,
            workflow_state=WorkflowState.ANALYTICS_PROCESSING,
        )

        warnings: list[str] = []

        # 1. Deduplicate & normalize news
        deduped_news = await self.call_tool(
            "normalize_and_deduplicate_news",
            {"articles": news_articles},
            context,
        )

        # 2. Compute aggregate sentiment
        agg_sentiment_dict = await self.call_tool(
            "aggregate_news_sentiment",
            {"symbol": symbol, "articles": deduped_news},
            context,
        )
        agg_sentiment = AggregateSentiment(**agg_sentiment_dict)

        # 3. Compute technical indicators
        tech_dict = await self.call_tool(
            "compute_technical_indicators",
            {"symbol": symbol, "observations": observations},
            context,
        )
        tech = TechnicalSnapshot(**tech_dict)

        # 4. Build research features
        features_dict = await self.call_tool(
            "build_research_features",
            {
                "symbol": symbol,
                "technical": tech,
                "sentiment": agg_sentiment,
                "benchmark": benchmark,
            },
            context,
        )
        rf = ResearchFeatures(**features_dict)

        # 5. Run Scorecard Signal Model
        sig_dict = await self.call_tool(
            "run_signal_model",
            {"features": rf, "method": "scorecard"},
            context,
        )
        sig = SignalResult(**sig_dict)

        return SentimentTechnicalAgentOutput(
            status="complete",
            technical_artifact=f"artifact://{request.run_id}/technical_indicators/{symbol}",
            sentiment_artifact=f"artifact://{request.run_id}/sentiment/{symbol}",
            features_artifact=f"artifact://{request.run_id}/research_features/{symbol}",
            signal_candidate=sig,
            warnings=warnings,
        )
