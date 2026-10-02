"""MCP contracts including tool context, role authorization, and request envelopes."""

from datetime import datetime
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


class AgentRole(str, Enum):
    MARKET_DATA = "Market Data Agent"
    SENTIMENT_TECHNICAL = "Sentiment & Technical Agent"
    SYNTHESIS_REPORT = "Synthesis & Report Agent"
    ORCHESTRATOR = "Orchestrator"


class WorkflowState(str, Enum):
    INITIALIZED = "INITIALIZED"
    DATA_COLLECTION = "DATA_COLLECTION"
    ANALYTICS_PROCESSING = "ANALYTICS_PROCESSING"
    SYNTHESIS = "SYNTHESIS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ToolContext(BaseModel):
    """Context required on every MCP invocation matching doc 05."""

    run_id: str
    analysis_timestamp: datetime
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    caller_role: AgentRole
    workflow_state: WorkflowState
    idempotency_key: str | None = None


class ProviderHealth(BaseModel):
    """Provider health status."""

    provider_name: str
    is_healthy: bool
    latency_ms: float
    rate_limit_remaining: int | None = None
    rate_limit_reset_seconds: int | None = None
    message: str = "OK"


class ArtifactMetadata(BaseModel):
    """Immutable artifact metadata record."""

    artifact_id: str
    artifact_ref: str
    artifact_kind: str
    run_id: str
    symbol: str | None = None
    created_at: datetime
    sha256_hash: str
    size_bytes: int
    content_type: str = "application/json"
