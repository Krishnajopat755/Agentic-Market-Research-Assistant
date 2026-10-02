"""Deterministic mock LLM adapter for offline CI, local execution, and agent testing."""

import re
from typing import Any, TypeVar

from pydantic import BaseModel

from src.llm.base import BaseLLMAdapter, LLMMessage, LLMResponse
from src.providers.indian_stocks import get_equity_metadata

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

        # Extract symbol from trace context or prompt
        symbol = "RELIANCE"
        if trace_context and trace_context.get("symbol"):
            symbol = trace_context["symbol"]
        else:
            # Try to extract from user message
            for m in reversed(messages):
                if m.role == "user":
                    match = re.search(r"for\s+([A-Za-z0-9_.^]+)", m.content)
                    if match:
                        symbol = match.group(1).strip()
                        break

        # Check if caller asks for structured output via schema
        if response_schema is not None:
            schema_name = response_schema.__name__

            if schema_name == "MarketDataAgentOutput":
                output_data = {
                    "status": "complete",
                    "market_artifacts": [f"artifact://market/bars/{symbol}"],
                    "news_artifacts": [f"artifact://news/raw/{symbol}"],
                    "freshness": {symbol: 120.0},
                    "session_status": {"IN": "OPEN", "US": "CLOSED"},
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
                    "technical_artifact": f"artifact://indicators/{symbol}",
                    "sentiment_artifact": f"artifact://sentiment/{symbol}",
                    "features_artifact": f"artifact://features/{symbol}",
                    "signal_candidate": {
                        "symbol": symbol,
                        "as_of": "2026-10-01T10:00:00Z",
                        "horizon_bars": 5,
                        "method": "scorecard",
                        "model_version": "scorecard-v1.0.0",
                        "state": "BULLISH",
                        "score": 0.28,
                        "confidence": 0.74,
                        "top_contributors": [],
                        "evidence_refs": [
                            f"artifact://indicators/{symbol}",
                            f"artifact://sentiment/{symbol}",
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
                # Parse parameters from user prompt text
                user_text = ""
                for m in reversed(messages):
                    if m.role == "user":
                        user_text = m.content
                        break

                meta = get_equity_metadata(symbol)
                company_name = meta["name"]
                sector = meta["sector"]
                clean_sym = symbol.split(".")[0].replace("^", "")

                # Parse metrics from prompt
                state_match = re.search(r"Market State:\s*([A-Za-z]+)", user_text)
                market_state = state_match.group(1).upper() if state_match else "BULLISH"

                score_match = re.search(r"Score:\s*([+-]?\d+\.?\d*)", user_text)
                signal_score = float(score_match.group(1)) if score_match else 0.28

                conf_match = re.search(r"Confidence:\s*(\d+\.?\d*)%?", user_text)
                confidence = (
                    (float(conf_match.group(1)) / 100.0 if float(conf_match.group(1)) > 1.0 else float(conf_match.group(1)))
                    if conf_match
                    else 0.74
                )

                ret_match = re.search(r"5d Return:\s*([+-]?\d+\.?\d*%?)", user_text)
                ret_5d = ret_match.group(1) if ret_match else "+1.8%"

                rsi_match = re.search(r"RSI:\s*([0-9.]+)", user_text)
                rsi_str = rsi_match.group(1) if rsi_match else "56.2"

                sent_match = re.search(r"Mean Sentiment:\s*([+-]?\d+\.?\d*)", user_text)
                sent_score = float(sent_match.group(1)) if sent_match else 0.32

                articles_match = re.search(r"over\s*(\d+)\s*articles", user_text)
                articles_count = int(articles_match.group(1)) if articles_match else 5

                # Generate dynamic context-specific headline and executive summary
                if market_state == "BULLISH":
                    headline = f"{company_name} Demonstrates Bullish Technical Setup with Positive Momentum in {sector}"
                    sent_desc = "constructive" if sent_score >= 0 else "resilient"
                    executive_summary = (
                        f"{clean_sym} ({company_name}) exhibits a confirmed bullish stance driven by healthy momentum "
                        f"(5-day return {ret_5d}), strong RSI regime ({rsi_str}), and {sent_desc} news sentiment "
                        f"({sent_score:+.2f}) across {articles_count} verified financial publications."
                    )
                elif market_state == "BEARISH":
                    headline = f"{company_name} Displays Cautious Technical Posture Amid Consolidation in {sector}"
                    sent_desc = "cautious" if sent_score < 0 else "mixed"
                    executive_summary = (
                        f"{clean_sym} ({company_name}) displays a defensive bearish posture reflecting recent price consolidation "
                        f"(5-day return {ret_5d}), softer RSI readings ({rsi_str}), and {sent_desc} news sentiment "
                        f"({sent_score:+.2f}) across {articles_count} recent market news reports."
                    )
                else:
                    headline = f"{company_name} Maintains Balanced Neutral Consolidation Across Key Moving Averages"
                    executive_summary = (
                        f"{clean_sym} ({company_name}) demonstrates a neutral equilibrium profile with steady price action "
                        f"(5-day return {ret_5d}), stable RSI equilibrium ({rsi_str}), and balanced news sentiment "
                        f"({sent_score:+.2f}) over {articles_count} recent publications."
                    )

                output_data = {
                    "status": "complete",
                    "headline": headline,
                    "market_state": market_state,
                    "signal_score": signal_score,
                    "confidence": confidence,
                    "executive_summary": executive_summary,
                    "key_evidence": [
                        {
                            "claim_id": "claim-01",
                            "claim_text": f"{company_name} registered a 5-day return of {ret_5d} with RSI at {rsi_str}.",
                            "evidence_type": "indicator",
                            "evidence_ref": f"artifact://indicators/{symbol}",
                        },
                        {
                            "claim_id": "claim-02",
                            "claim_text": f"Financial media sentiment averaged {sent_score:+.2f} across {articles_count} analyzed news articles.",
                            "evidence_type": "news",
                            "evidence_ref": f"artifact://news/{symbol}",
                        },
                    ],
                    "caveats": [
                        f"Quantitative scorecard signal for {clean_sym} is a research indicator based on historical indicators and sentiment.",
                        f"Market volatility in {meta['exchange']} index components can impact short-term technical horizon targets.",
                    ],
                    "report_ref": f"artifact://report/{symbol}",
                }
                validated = response_schema(**output_data)
                return LLMResponse(
                    content=validated.model_dump_json(),
                    structured_output=validated.model_dump(),
                    usage_tokens={"prompt_tokens": 200, "completion_tokens": 120},
                )

        # Default fallback text
        return LLMResponse(
            content=f"Analysis complete for {symbol}.",
            usage_tokens={"prompt_tokens": 50, "completion_tokens": 10},
        )
