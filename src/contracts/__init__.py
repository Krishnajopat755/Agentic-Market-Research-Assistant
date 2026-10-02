"""Export all contracts."""

from src.contracts.analysis import AnalysisRequest
from src.contracts.errors import ErrorCode, ErrorEnvelope, FinanceAppException
from src.contracts.evidence import ClaimValidationResult, ResearchEvidence
from src.contracts.features import ResearchFeatures
from src.contracts.market import MarketCalendar, MarketObservation, MarketSnapshot
from src.contracts.mcp import (
    AgentRole,
    ArtifactMetadata,
    ProviderHealth,
    ToolContext,
    WorkflowState,
)
from src.contracts.news import AggregateSentiment, NewsArticle, SentimentScore
from src.contracts.report import DailyResearchReport
from src.contracts.signal import (
    SignalContributor,
    SignalResult,
    WalkForwardEvaluationResult,
)

__all__ = [
    "AgentRole",
    "AggregateSentiment",
    "AnalysisRequest",
    "ArtifactMetadata",
    "ClaimValidationResult",
    "DailyResearchReport",
    "ErrorCode",
    "ErrorEnvelope",
    "FinanceAppException",
    "MarketCalendar",
    "MarketObservation",
    "MarketSnapshot",
    "NewsArticle",
    "ProviderHealth",
    "ResearchEvidence",
    "ResearchFeatures",
    "SentimentScore",
    "SignalContributor",
    "SignalResult",
    "ToolContext",
    "WalkForwardEvaluationResult",
    "WorkflowState",
]
