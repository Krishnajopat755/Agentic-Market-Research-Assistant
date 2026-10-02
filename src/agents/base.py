"""Agent base class and structured output contracts."""

from abc import ABC
from typing import Any

from pydantic import BaseModel, Field

from services.finance_mcp.server import FinanceMCPServer
from src.contracts.evidence import ResearchEvidence
from src.contracts.mcp import AgentRole, ToolContext, WorkflowState
from src.contracts.signal import SignalResult


class MarketDataAgentOutput(BaseModel):
    status: str = Field(default="complete", description="complete, blocked, or degraded")
    market_artifacts: list[str] = Field(default_factory=list)
    news_artifacts: list[str] = Field(default_factory=list)
    freshness: dict[str, float] = Field(default_factory=dict)
    session_status: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class SentimentTechnicalAgentOutput(BaseModel):
    status: str = Field(default="complete")
    technical_artifact: str | None = None
    sentiment_artifact: str | None = None
    features_artifact: str | None = None
    signal_candidate: SignalResult | None = None
    warnings: list[str] = Field(default_factory=list)


class SynthesisReportAgentOutput(BaseModel):
    status: str = Field(default="complete")
    headline: str
    market_state: str
    signal_score: float
    confidence: float
    executive_summary: str
    key_evidence: list[ResearchEvidence] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)
    report_ref: str | None = None


class BaseAgent(ABC):
    """Abstract base agent communicating exclusively via Finance MCP server tools."""

    def __init__(self, mcp_server: FinanceMCPServer, role: AgentRole):
        self.mcp = mcp_server
        self.role = role

    def create_context(
        self,
        run_id: str,
        analysis_timestamp: Any,
        workflow_state: WorkflowState,
        idempotency_key: str | None = None,
    ) -> ToolContext:
        return ToolContext(
            run_id=run_id,
            analysis_timestamp=analysis_timestamp,
            caller_role=self.role,
            workflow_state=workflow_state,
            idempotency_key=idempotency_key,
        )

    async def call_tool(
        self, tool_name: str, arguments: dict[str, Any], context: ToolContext
    ) -> Any:
        res = await self.mcp.execute_tool(tool_name, arguments, context)
        if res.get("status") == "error":
            from src.contracts.errors import ErrorCode, FinanceAppException

            err = res.get("error", {})
            raise FinanceAppException(
                error_code=ErrorCode(err.get("error_code", "PROVIDER_UNAVAILABLE")),
                message=err.get("message", "Tool execution error"),
                retryable=err.get("retryable", False),
                retry_after_seconds=err.get("retry_after_seconds"),
                details=err.get("details", {}),
            )
        return res.get("result")
