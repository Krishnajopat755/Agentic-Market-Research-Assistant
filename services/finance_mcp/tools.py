"""Implementation of the typed Finance MCP tool catalog."""

from collections.abc import Sequence
from datetime import datetime, timedelta
from typing import Any

from services.finance_mcp.auth import authorize_tool_invocation
from src.contracts.evidence import ClaimValidationResult, ResearchEvidence
from src.contracts.features import ResearchFeatures
from src.contracts.market import MarketCalendar, MarketObservation, MarketSnapshot
from src.contracts.mcp import ArtifactMetadata, ProviderHealth, ToolContext
from src.contracts.news import AggregateSentiment, NewsArticle, SentimentScore
from src.contracts.report import DailyResearchReport
from src.contracts.signal import SignalResult, WalkForwardEvaluationResult
from src.contracts.technical import TechnicalSnapshot
from src.finance_core.evaluation.walk_forward import run_walk_forward_evaluation
from src.finance_core.features.builder import build_research_features as core_build_features
from src.finance_core.indicators.technical import (
    compute_technical_indicators as core_compute_indicators,
)
from src.finance_core.market_data.normalization import normalize_datetime
from src.finance_core.news.deduplication import deduplicate_news
from src.finance_core.news.normalization import filter_news_point_in_time
from src.finance_core.sentiment.aggregator import aggregate_sentiment as core_aggregate_sentiment
from src.finance_core.sentiment.dictionary import FinancialLexiconSentimentModel
from src.finance_core.signal.scorecard import compute_scorecard_signal
from src.observability.logging import get_logger
from src.observability.tracing import default_tracer
from src.providers.base import BaseMarketDataProvider, BaseNewsProvider
from src.services_registry import AppServices

logger = get_logger("finance_mcp_tools")


class FinanceMCPTools:
    """Finance MCP tool handlers with authorization, idempotency, and storage lineage."""

    def __init__(self, services: AppServices):
        self.services = services
        self.market_provider: BaseMarketDataProvider = services.market_provider
        self.news_provider: BaseNewsProvider = services.news_provider
        self.storage = services.storage
        self.repo = services.repo
        self.sentiment_model = FinancialLexiconSentimentModel()
        self._idempotency_cache: dict[str, Any] = {}

    def _check_idempotency(self, tool_name: str, context: ToolContext, payload: Any) -> Any | None:
        if not context.idempotency_key:
            return None
        cache_key = f"{tool_name}:{context.idempotency_key}"
        return self._idempotency_cache.get(cache_key)

    def _save_idempotency(self, tool_name: str, context: ToolContext, result: Any) -> None:
        if context.idempotency_key:
            cache_key = f"{tool_name}:{context.idempotency_key}"
            self._idempotency_cache[cache_key] = result

    # 1. Symbol & Market
    async def resolve_symbol(self, symbol: str, context: ToolContext) -> dict[str, str]:
        authorize_tool_invocation("resolve_symbol", context)
        with default_tracer.start_span(
            "mcp.resolve_symbol", attributes={"symbol": symbol, "run_id": context.run_id}
        ):
            return await self.market_provider.resolve_symbol(symbol)

    async def fetch_market_snapshot(self, symbol: str, context: ToolContext) -> MarketSnapshot:
        authorize_tool_invocation("fetch_market_snapshot", context)
        cached = self._check_idempotency("fetch_market_snapshot", context, symbol)
        if cached:
            return cached

        with default_tracer.start_span(
            "mcp.fetch_market_snapshot", attributes={"symbol": symbol, "run_id": context.run_id}
        ):
            snapshot = await self.market_provider.get_snapshot(
                symbol, as_of=context.analysis_timestamp
            )
            meta = self.storage.store_json(
                kind="market_snapshot",
                data=snapshot,
                run_id=context.run_id,
                symbol=symbol,
            )
            self.repo.add_artifact(context.run_id, meta)
            self._save_idempotency("fetch_market_snapshot", context, snapshot)
            return snapshot

    async def fetch_historical_bars(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        context: ToolContext,
        interval: str = "daily",
    ) -> list[MarketObservation]:
        authorize_tool_invocation("fetch_historical_bars", context)
        # Point-in-time rule: end cannot exceed context.analysis_timestamp
        effective_end = min(normalize_datetime(end), normalize_datetime(context.analysis_timestamp))

        with default_tracer.start_span(
            "mcp.fetch_historical_bars", attributes={"symbol": symbol, "run_id": context.run_id}
        ):
            bars = await self.market_provider.get_historical_bars(
                symbol=symbol,
                start=start,
                end=effective_end,
                interval=interval,
            )
            meta = self.storage.store_json(
                kind="raw_market",
                data=bars,
                run_id=context.run_id,
                symbol=symbol,
            )
            self.repo.add_artifact(context.run_id, meta)
            return bars

    async def fetch_market_benchmark(
        self,
        context: ToolContext,
        symbol: str = "SPY",
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[MarketObservation]:
        authorize_tool_invocation("fetch_market_benchmark", context)
        effective_end = min(
            normalize_datetime(end or context.analysis_timestamp),
            normalize_datetime(context.analysis_timestamp),
        )
        with default_tracer.start_span(
            "mcp.fetch_market_benchmark", attributes={"symbol": symbol, "run_id": context.run_id}
        ):
            return await self.market_provider.get_benchmark(
                symbol=symbol, start=start, end=effective_end
            )

    async def fetch_market_calendar(self, context: ToolContext) -> MarketCalendar:
        authorize_tool_invocation("fetch_market_calendar", context)
        with default_tracer.start_span(
            "mcp.fetch_market_calendar", attributes={"run_id": context.run_id}
        ):
            return await self.market_provider.get_calendar(as_of=context.analysis_timestamp)

    # 2. News
    async def fetch_market_news(
        self,
        symbols: list[str],
        context: ToolContext,
        lookback_hours: int = 24,
        limit: int = 50,
    ) -> list[NewsArticle]:
        authorize_tool_invocation("fetch_market_news", context)
        end_utc = normalize_datetime(context.analysis_timestamp)
        start_utc = end_utc - timedelta(hours=lookback_hours)

        with default_tracer.start_span(
            "mcp.fetch_market_news", attributes={"symbols": symbols, "run_id": context.run_id}
        ):
            articles = await self.news_provider.get_news(
                symbols=symbols,
                start=start_utc,
                end=end_utc,
                limit=limit,
            )
            meta = self.storage.store_json(
                kind="raw_news",
                data=articles,
                run_id=context.run_id,
                symbol=",".join(symbols),
            )
            self.repo.add_artifact(context.run_id, meta)
            return articles

    async def normalize_and_deduplicate_news(
        self,
        articles: Sequence[NewsArticle],
        context: ToolContext,
    ) -> list[NewsArticle]:
        authorize_tool_invocation("normalize_and_deduplicate_news", context)
        articles = [NewsArticle(**a) if isinstance(a, dict) else a for a in articles]
        with default_tracer.start_span(
            "mcp.normalize_and_deduplicate_news", attributes={"run_id": context.run_id}
        ):
            # Filter strictly point-in-time
            filtered = filter_news_point_in_time(articles, as_of=context.analysis_timestamp)
            canonical, all_tagged = deduplicate_news(filtered)
            meta = self.storage.store_json(
                kind="normalized_news",
                data=all_tagged,
                run_id=context.run_id,
            )
            self.repo.add_artifact(context.run_id, meta)
            return all_tagged

    # 3. Sentiment
    async def compute_sentiment(
        self,
        text: str,
        context: ToolContext,
        entity: str | None = None,
    ) -> SentimentScore:
        authorize_tool_invocation("compute_sentiment", context)
        with default_tracer.start_span(
            "mcp.compute_sentiment", attributes={"run_id": context.run_id}
        ):
            return self.sentiment_model.score(text, entity=entity)

    async def aggregate_news_sentiment(
        self,
        symbol: str,
        articles: Sequence[NewsArticle],
        context: ToolContext,
    ) -> AggregateSentiment:
        authorize_tool_invocation("aggregate_news_sentiment", context)
        articles = [NewsArticle(**a) if isinstance(a, dict) else a for a in articles]
        with default_tracer.start_span(
            "mcp.aggregate_news_sentiment", attributes={"symbol": symbol, "run_id": context.run_id}
        ):
            # Score each article if not scored
            scored_articles: list[NewsArticle] = []
            for art in articles:
                if not art.sentiment:
                    txt = f"{art.title}. {art.description or ''}"
                    sent = self.sentiment_model.score(txt, entity=symbol)
                    art = art.model_copy(update={"sentiment": sent})
                scored_articles.append(art)

            agg = core_aggregate_sentiment(
                symbol, scored_articles, as_of=context.analysis_timestamp
            )
            meta = self.storage.store_json(
                kind="sentiment",
                data=agg,
                run_id=context.run_id,
                symbol=symbol,
            )
            self.repo.add_artifact(context.run_id, meta)
            return agg

    # 4. Technical
    async def compute_technical_indicators(
        self,
        symbol: str,
        observations: Sequence[MarketObservation],
        context: ToolContext,
    ) -> TechnicalSnapshot:
        authorize_tool_invocation("compute_technical_indicators", context)
        observations = [MarketObservation(**o) if isinstance(o, dict) else o for o in observations]
        with default_tracer.start_span(
            "mcp.compute_technical_indicators",
            attributes={"symbol": symbol, "run_id": context.run_id},
        ):
            tech = core_compute_indicators(symbol, observations, as_of=context.analysis_timestamp)
            meta = self.storage.store_json(
                kind="technical_indicators",
                data=tech,
                run_id=context.run_id,
                symbol=symbol,
            )
            self.repo.add_artifact(context.run_id, meta)
            return tech

    # 5. Features & Signals
    async def build_research_features(
        self,
        symbol: str,
        technical: TechnicalSnapshot,
        sentiment: AggregateSentiment,
        context: ToolContext,
        benchmark: Sequence[MarketObservation] | None = None,
    ) -> ResearchFeatures:
        authorize_tool_invocation("build_research_features", context)
        if isinstance(technical, dict):
            technical = TechnicalSnapshot(**technical)
        if isinstance(sentiment, dict):
            sentiment = AggregateSentiment(**sentiment)
        if benchmark:
            benchmark = [MarketObservation(**b) if isinstance(b, dict) else b for b in benchmark]
        with default_tracer.start_span(
            "mcp.build_research_features", attributes={"symbol": symbol, "run_id": context.run_id}
        ):
            rf = core_build_features(
                symbol=symbol,
                as_of=context.analysis_timestamp,
                technical=technical,
                sentiment=sentiment,
                benchmark_observations=benchmark,
            )
            meta = self.storage.store_json(
                kind="research_features",
                data=rf,
                run_id=context.run_id,
                symbol=symbol,
            )
            rf.artifact_ref = meta.artifact_ref
            self.repo.add_artifact(context.run_id, meta)
            return rf

    async def run_signal_model(
        self,
        features: ResearchFeatures,
        context: ToolContext,
        method: str = "scorecard",
    ) -> SignalResult:
        authorize_tool_invocation("run_signal_model", context)
        if isinstance(features, dict):
            features = ResearchFeatures(**features)
        with default_tracer.start_span(
            "mcp.run_signal_model", attributes={"symbol": features.symbol, "run_id": context.run_id}
        ):
            sig = compute_scorecard_signal(features)
            meta = self.storage.store_json(
                kind="signal",
                data=sig,
                run_id=context.run_id,
                symbol=features.symbol,
            )
            self.repo.add_artifact(context.run_id, meta)
            return sig

    async def evaluate_signal_model_historical(
        self,
        symbol: str,
        observations: Sequence[MarketObservation],
        context: ToolContext,
    ) -> WalkForwardEvaluationResult:
        authorize_tool_invocation("evaluate_signal_model_historical", context)
        with default_tracer.start_span(
            "mcp.evaluate_signal_model_historical",
            attributes={"symbol": symbol, "run_id": context.run_id},
        ):
            res = run_walk_forward_evaluation(observations)
            meta = self.storage.store_json(
                kind="historical_evaluation",
                data=res,
                run_id=context.run_id,
                symbol=symbol,
            )
            self.repo.add_artifact(context.run_id, meta)
            return res

    async def compare_signal_candidates(
        self,
        candidates: list[SignalResult],
        context: ToolContext,
    ) -> dict[str, Any]:
        authorize_tool_invocation("compare_signal_candidates", context)
        with default_tracer.start_span(
            "mcp.compare_signal_candidates", attributes={"run_id": context.run_id}
        ):
            consensus = "NEUTRAL"
            scores = [c.score for c in candidates]
            mean_score = sum(scores) / len(scores) if scores else 0.0
            if mean_score >= 0.20:
                consensus = "BULLISH"
            elif mean_score <= -0.20:
                consensus = "BEARISH"
            return {
                "consensus_state": consensus,
                "mean_score": round(mean_score, 4),
                "candidates_count": len(candidates),
                "methods": [c.method for c in candidates],
            }

    # 6. Evidence & Reporting
    async def get_research_evidence(
        self,
        symbol: str,
        context: ToolContext,
    ) -> list[ResearchEvidence]:
        authorize_tool_invocation("get_research_evidence", context)
        # Collect references from storage and repository
        evidence_list: list[ResearchEvidence] = []
        run = self.repo.get_run(context.run_id)
        if run:
            for art in run.artifacts:
                if not art.symbol or art.symbol.upper() == symbol.upper():
                    evidence_list.append(
                        ResearchEvidence(
                            claim_id=f"ev-{art.artifact_id}",
                            claim_text=f"Derived from {art.artifact_kind} artifact ({art.sha256_hash[:8]})",
                            evidence_type=art.artifact_kind,
                            evidence_ref=art.artifact_ref,
                            source_timestamp=art.created_at,
                        )
                    )
        return evidence_list

    async def validate_report_claims(
        self,
        claims: list[ResearchEvidence],
        context: ToolContext,
    ) -> ClaimValidationResult:
        authorize_tool_invocation("validate_report_claims", context)
        claims = [ResearchEvidence(**c) if isinstance(c, dict) else c for c in claims]
        # Check that each claim has a valid artifact_ref or source_url
        unsupported: list[str] = []
        for c in claims:
            if not c.evidence_ref and not c.source_url:
                unsupported.append(c.claim_text)

        is_valid = len(unsupported) == 0
        return ClaimValidationResult(
            is_valid=is_valid,
            total_claims=len(claims),
            verified_claims=len(claims) - len(unsupported),
            unsupported_claims=unsupported,
        )

    async def render_daily_report(
        self,
        report: DailyResearchReport,
        context: ToolContext,
        format_type: str = "markdown",
    ) -> str:
        authorize_tool_invocation("render_daily_report", context)
        if isinstance(report, dict):
            report = DailyResearchReport(**report)
        from src.finance_core.reporting.renderer import render_report

        return render_report(report, format_type=format_type)

    async def persist_research_record(
        self,
        report: DailyResearchReport,
        context: ToolContext,
    ) -> dict[str, str]:
        authorize_tool_invocation("persist_research_record", context)
        if isinstance(report, dict):
            report = DailyResearchReport(**report)
        meta = self.storage.store_json(
            kind="report",
            data=report,
            run_id=context.run_id,
            symbol=report.symbol,
        )
        self.repo.save_report(context.run_id, report.symbol, report)
        self.repo.add_artifact(context.run_id, meta)
        return {"status": "saved", "artifact_ref": meta.artifact_ref, "sha256": meta.sha256_hash}

    # 7. Operational
    async def get_provider_health(self, context: ToolContext) -> list[ProviderHealth]:
        authorize_tool_invocation("get_provider_health", context)
        m_health = await self.market_provider.get_health()
        n_health = await self.news_provider.get_health()
        return [m_health, n_health]

    async def get_artifact_metadata(
        self,
        artifact_ref: str,
        context: ToolContext,
    ) -> ArtifactMetadata | None:
        authorize_tool_invocation("get_artifact_metadata", context)
        run = self.repo.get_run(context.run_id)
        if run:
            for art in run.artifacts:
                if art.artifact_ref == artifact_ref or art.artifact_id in artifact_ref:
                    return art
        return None
