"""Server-side authorization and workflow state enforcement for MCP tools."""

from src.contracts.errors import ErrorCode, FinanceAppException
from src.contracts.mcp import AgentRole, ToolContext, WorkflowState

# Strict authorization matrix matching Section 4 of docs/05_MCP_SERVER_SPEC.md
ROLE_TOOL_ALLOWLIST: dict[AgentRole, set[str]] = {
    AgentRole.MARKET_DATA: {
        "resolve_symbol",
        "fetch_market_snapshot",
        "fetch_historical_bars",
        "fetch_market_benchmark",
        "fetch_market_calendar",
        "fetch_market_news",
        "get_provider_health",
        "get_artifact_metadata",
    },
    AgentRole.SENTIMENT_TECHNICAL: {
        "normalize_and_deduplicate_news",
        "compute_sentiment",
        "aggregate_news_sentiment",
        "compute_technical_indicators",
        "build_research_features",
        "run_signal_model",
        "evaluate_signal_model_historical",
        "get_artifact_metadata",
        "get_provider_health",
    },
    AgentRole.SYNTHESIS_REPORT: {
        "get_research_evidence",
        "compare_signal_candidates",
        "validate_report_claims",
        "render_daily_report",
        "persist_research_record",
        "get_artifact_metadata",
    },
    AgentRole.ORCHESTRATOR: {
        # Orchestrator has supervisory access to all tools
        "resolve_symbol",
        "fetch_market_snapshot",
        "fetch_historical_bars",
        "fetch_market_benchmark",
        "fetch_market_calendar",
        "fetch_market_news",
        "normalize_and_deduplicate_news",
        "compute_sentiment",
        "aggregate_news_sentiment",
        "compute_technical_indicators",
        "build_research_features",
        "run_signal_model",
        "evaluate_signal_model_historical",
        "compare_signal_candidates",
        "get_research_evidence",
        "validate_report_claims",
        "render_daily_report",
        "persist_research_record",
        "get_provider_health",
        "get_artifact_metadata",
    },
}

REQUIRED_WORKFLOW_STATE: dict[str, list[WorkflowState]] = {
    "fetch_market_snapshot": [WorkflowState.INITIALIZED, WorkflowState.DATA_COLLECTION],
    "fetch_historical_bars": [WorkflowState.INITIALIZED, WorkflowState.DATA_COLLECTION],
    "fetch_market_news": [WorkflowState.INITIALIZED, WorkflowState.DATA_COLLECTION],
    "compute_technical_indicators": [
        WorkflowState.DATA_COLLECTION,
        WorkflowState.ANALYTICS_PROCESSING,
    ],
    "normalize_and_deduplicate_news": [
        WorkflowState.DATA_COLLECTION,
        WorkflowState.ANALYTICS_PROCESSING,
    ],
    "compute_sentiment": [WorkflowState.ANALYTICS_PROCESSING],
    "build_research_features": [WorkflowState.ANALYTICS_PROCESSING],
    "run_signal_model": [WorkflowState.ANALYTICS_PROCESSING],
    "render_daily_report": [WorkflowState.SYNTHESIS, WorkflowState.COMPLETED],
    "persist_research_record": [WorkflowState.SYNTHESIS, WorkflowState.COMPLETED],
}


def authorize_tool_invocation(tool_name: str, context: ToolContext) -> None:
    """
    Enforce Rule 3 & AR-04:
    Verify that the calling role is authorized for the tool,
    and that the current workflow state permits this action.
    """
    allowed_tools = ROLE_TOOL_ALLOWLIST.get(context.caller_role, set())
    if tool_name not in allowed_tools:
        raise FinanceAppException(
            error_code=ErrorCode.TOOL_NOT_AUTHORIZED,
            message=(
                f"Role '{context.caller_role.value}' is not authorized to call '{tool_name}'. "
                f"Allowed tools: {sorted(list(allowed_tools))}"
            ),
            details={"role": context.caller_role.value, "tool": tool_name},
        )

    # State check (if caller is not Orchestrator)
    if context.caller_role != AgentRole.ORCHESTRATOR and tool_name in REQUIRED_WORKFLOW_STATE:
        valid_states = REQUIRED_WORKFLOW_STATE[tool_name]
        if context.workflow_state not in valid_states:
            raise FinanceAppException(
                error_code=ErrorCode.STATE_PRECONDITION_FAILED,
                message=(
                    f"Tool '{tool_name}' cannot be called in state '{context.workflow_state.value}'. "
                    f"Required state: {[s.value for s in valid_states]}"
                ),
                details={"current_state": context.workflow_state.value, "tool": tool_name},
            )
