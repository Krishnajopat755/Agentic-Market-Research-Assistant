"""Finance MCP Server exposing typed tools via stdio or HTTP dispatch."""

from collections.abc import Callable, Coroutine
from typing import Any

from services.finance_mcp.tools import FinanceMCPTools
from src.contracts.errors import ErrorCode, ErrorEnvelope, FinanceAppException
from src.contracts.mcp import ToolContext
from src.observability.logging import get_logger
from src.services_registry import AppServices, create_default_services

logger = get_logger("finance_mcp_server")


class FinanceMCPServer:
    """Finance MCP Server coordinating typed tool execution, authorization, and error handling."""

    def __init__(self, services: AppServices | None = None):
        self.services = services or create_default_services(mode="fixture")
        self.tools = FinanceMCPTools(self.services)
        self._tool_registry: dict[str, Callable[..., Coroutine[Any, Any, Any]]] = {
            "resolve_symbol": self.tools.resolve_symbol,
            "fetch_market_snapshot": self.tools.fetch_market_snapshot,
            "fetch_historical_bars": self.tools.fetch_historical_bars,
            "fetch_market_benchmark": self.tools.fetch_market_benchmark,
            "fetch_market_calendar": self.tools.fetch_market_calendar,
            "fetch_market_news": self.tools.fetch_market_news,
            "normalize_and_deduplicate_news": self.tools.normalize_and_deduplicate_news,
            "compute_sentiment": self.tools.compute_sentiment,
            "aggregate_news_sentiment": self.tools.aggregate_news_sentiment,
            "compute_technical_indicators": self.tools.compute_technical_indicators,
            "build_research_features": self.tools.build_research_features,
            "run_signal_model": self.tools.run_signal_model,
            "evaluate_signal_model_historical": self.tools.evaluate_signal_model_historical,
            "compare_signal_candidates": self.tools.compare_signal_candidates,
            "get_research_evidence": self.tools.get_research_evidence,
            "validate_report_claims": self.tools.validate_report_claims,
            "render_daily_report": self.tools.render_daily_report,
            "persist_research_record": self.tools.persist_research_record,
            "get_provider_health": self.tools.get_provider_health,
            "get_artifact_metadata": self.tools.get_artifact_metadata,
        }

    def list_tools(self) -> list[str]:
        return sorted(list(self._tool_registry.keys()))

    async def execute_tool(
        self, tool_name: str, arguments: dict[str, Any], context: ToolContext
    ) -> dict[str, Any]:
        """
        Execute tool call with strict boundary validation, error envelopes, and audit logging.
        """
        if tool_name not in self._tool_registry:
            raise FinanceAppException(
                error_code=ErrorCode.TOOL_NOT_AUTHORIZED,
                message=f"Tool '{tool_name}' does not exist in Finance MCP Server catalog",
            )

        handler = self._tool_registry[tool_name]
        try:
            # Inject context
            args = dict(arguments)
            args["context"] = context
            result = await handler(**args)

            # Serialize output
            if hasattr(result, "model_dump"):
                out = result.model_dump(mode="json")
            elif isinstance(result, list):
                out = [
                    item.model_dump(mode="json") if hasattr(item, "model_dump") else item
                    for item in result
                ]
            else:
                out = result

            return {"status": "success", "result": out}

        except FinanceAppException as fe:
            logger.warning(
                f"MCP Tool Exception on {tool_name}: {fe.envelope.error_code} - {fe.envelope.message}",
                extra={
                    "tool": tool_name,
                    "error_code": fe.envelope.error_code.value,
                    "run_id": context.run_id,
                },
            )
            return {"status": "error", "error": fe.to_dict()}
        except Exception as e:
            logger.exception(f"Unexpected error executing {tool_name}: {e!s}")
            env = ErrorEnvelope(
                error_code=ErrorCode.PROVIDER_UNAVAILABLE,
                message=f"Internal tool error during {tool_name}: {e!s}",
                details={"exception": str(e)},
            )
            return {"status": "error", "error": env.model_dump()}
