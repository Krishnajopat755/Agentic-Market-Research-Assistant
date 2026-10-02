"""Run repository and audit ledger implementation."""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from src.contracts.analysis import AnalysisRequest
from src.contracts.mcp import ArtifactMetadata, WorkflowState
from src.contracts.report import DailyResearchReport


class AuditEvent(BaseModel):
    """Immutable audit record of actions taken during a research run."""

    event_id: str
    run_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    actor: str  # agent name or orchestrator
    action: str  # tool called or state transition
    input_summary: dict[str, Any] | None = None
    output_summary: dict[str, Any] | None = None
    error_code: str | None = None
    duration_ms: float | None = None


class RunRecord(BaseModel):
    """Comprehensive persistence record of a research run."""

    run_id: str
    request: AnalysisRequest
    state: WorkflowState
    created_at: datetime
    updated_at: datetime
    audit_events: list[AuditEvent] = Field(default_factory=list)
    artifacts: list[ArtifactMetadata] = Field(default_factory=list)
    reports: dict[str, DailyResearchReport] = Field(default_factory=dict)
    errors: list[dict[str, Any]] = Field(default_factory=list)


class ResearchRepository:
    """Thread-safe in-memory and file-backed repository for runs and audit trails."""

    def __init__(self):
        self._runs: dict[str, RunRecord] = {}

    def create_run(self, request: AnalysisRequest) -> RunRecord:
        now = datetime.now(UTC)
        record = RunRecord(
            run_id=request.run_id,
            request=request,
            state=WorkflowState.INITIALIZED,
            created_at=now,
            updated_at=now,
        )
        self._runs[request.run_id] = record
        return record

    def get_run(self, run_id: str) -> RunRecord | None:
        return self._runs.get(run_id)

    def update_state(self, run_id: str, new_state: WorkflowState) -> None:
        if run_id in self._runs:
            self._runs[run_id].state = new_state
            self._runs[run_id].updated_at = datetime.now(UTC)

    def log_audit(self, event: AuditEvent) -> None:
        if event.run_id in self._runs:
            self._runs[event.run_id].audit_events.append(event)
            self._runs[event.run_id].updated_at = datetime.now(UTC)

    def add_artifact(self, run_id: str, metadata: ArtifactMetadata) -> None:
        if run_id in self._runs:
            self._runs[run_id].artifacts.append(metadata)

    def save_report(self, run_id: str, symbol: str, report: DailyResearchReport) -> None:
        if run_id in self._runs:
            self._runs[run_id].reports[symbol] = report
