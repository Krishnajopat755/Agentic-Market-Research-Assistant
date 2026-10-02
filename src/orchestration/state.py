"""Workflow state machine and context container."""

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from src.contracts.analysis import AnalysisRequest
from src.contracts.market import MarketObservation, MarketSnapshot
from src.contracts.mcp import WorkflowState
from src.contracts.news import AggregateSentiment, NewsArticle
from src.contracts.report import DailyResearchReport
from src.contracts.signal import SignalResult
from src.contracts.technical import TechnicalSnapshot


class SymbolWorkflowState(BaseModel):
    """Execution state and intermediate results for a single symbol."""

    symbol: str
    snapshot: MarketSnapshot | None = None
    bars: list[MarketObservation] = Field(default_factory=list)
    news: list[NewsArticle] = Field(default_factory=list)
    technical: TechnicalSnapshot | None = None
    sentiment: AggregateSentiment | None = None
    signal: SignalResult | None = None
    report: DailyResearchReport | None = None
    errors: list[str] = Field(default_factory=list)


class ResearchRunContext(BaseModel):
    """Top-level orchestrated execution state."""

    run_id: str
    request: AnalysisRequest
    state: WorkflowState = WorkflowState.INITIALIZED
    symbols_data: dict[str, SymbolWorkflowState] = Field(default_factory=dict)
    benchmark_bars: list[MarketObservation] = Field(default_factory=list)
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
