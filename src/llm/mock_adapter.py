"""Deterministic mock LLM adapter for offline CI and agent testing."""

from typing import Any, TypeVar

from pydantic import BaseModel

from src.llm.base import BaseLLMAdapter, LLMMessage, LLMResponse

T = TypeVar("T", bound=BaseModel)


class MockLLMAdapter(BaseLLMAdapter):
    """Deterministic LLM adapter designed to follow agentic tool calling and structured output contracts."""

    def __init__(self, mode: str = "orchestrated"):
        self.mode = mode
        self.call_history: list[list[LLMMessage]] = []

    async def complete(
        self,
        messages: list[LLMMessage],
        tools: list[dict[str, Any]] | None = None,
        response_schema: type[T] | None = None,
        trace_context: dict[str, Any] | None = None,
    ) -> LLMResponse:
        self.call_history.append(messages)

        # Check if caller asks for structured output via schema
        if response_schema is not None:
            schema_name = response_schema.__name__

            if schema_name == "MarketDataAgentOutput":
                output_data = {
                    "status": "complete",
                    "market_artifacts": ["artifact://market/bars/AAPL"],
                    "news_artifacts": ["artifact://news/raw/AAPL"],
                    "freshness": {"AAPL": 3600.0},
                    "session_status": {"US": "CLOSED"},
                    "warnings": [],
                }
                validated = response_schema(**output_data)
                return LLMResponse(
                    content=validated.model_dump_json(),
                    structured_output=validated.model_dump(),
                    usage_tokens={"prompt_tokens": 120, "completion_tokens": 60},
                )

            elif schema_name == "SentimentTechnicalAgentOutput":
                output_data = {
                    "status": "complete",
                    "technical_artifact": "artifact://indicators/AAPL",
                    "sentiment_artifact": "artifact://sentiment/AAPL",
                    "features_artifact": "artifact://features/AAPL",
                    "signal_candidate": {
                        "symbol": "AAPL",
                        "as_of": "2026-09-25T16:10:00Z",
                        "horizon_bars": 5,
                        "method": "scorecard",
                        "model_version": "scorecard-v1.0.0",
                        "state": "BULLISH",
                        "score": 0.28,
                        "confidence": 0.72,
                        "top_contributors": [],
                        "evidence_refs": [
                            "artifact://indicators/AAPL",
                            "artifact://sentiment/AAPL",
                        ],
                        "limitations": [],
                    },
                    "warnings": [],
                }
                validated = response_schema(**output_data)
                return LLMResponse(
                    content=validated.model_dump_json(),
                    structured_output=validated.model_dump(),
                    usage_tokens={"prompt_tokens": 150, "completion_tokens": 80},
                )

            elif schema_name == "SynthesisReportAgentOutput":
                output_data = {
                    "status": "complete",
                    "headline": "Apple Demonstrates Bullish Technical Setup Backed by Record Services Revenue",
                    "market_state": "BULLISH",
                    "signal_score": 0.28,
                    "confidence": 0.72,
                    "executive_summary": (
                        "AAPL exhibits a confirmed bullish stance driven by healthy momentum (5-day return +2.8%), "
                        "strong RSI regime (58.4), and constructive news sentiment (+0.38) following record Q4 services growth."
                    ),
                    "key_evidence": [
                        {
                            "claim_id": "claim-01",
                            "claim_text": "Apple posted positive 5-day price momentum above 20-day and 50-day moving averages.",
                            "evidence_type": "indicator",
                            "evidence_ref": "artifact://indicators/AAPL",
                        },
                        {
                            "claim_id": "claim-02",
                            "claim_text": "Financial news sentiment is positive (+0.38) following quarterly earnings beat.",
                            "evidence_type": "news",
                            "evidence_ref": "artifact://news/AAPL",
                        },
                    ],
                    "caveats": [
                        "Realized 20-day volatility is 24.5%, indicating active trading ranges.",
                        "Scorecard signal is a research indicator and not a financial guarantee.",
                    ],
                    "report_ref": "artifact://report/AAPL",
                }
                validated = response_schema(**output_data)
                return LLMResponse(
                    content=validated.model_dump_json(),
                    structured_output=validated.model_dump(),
                    usage_tokens={"prompt_tokens": 200, "completion_tokens": 120},
                )

        # Default fallback text
        return LLMResponse(
            content="Analysis complete.",
            usage_tokens={"prompt_tokens": 50, "completion_tokens": 10},
        )
