"""Anthropic Claude adapter implementation."""

import json
import os
from typing import Any, TypeVar

import httpx
from pydantic import BaseModel

from src.contracts.errors import ErrorCode, FinanceAppException
from src.llm.base import BaseLLMAdapter, LLMMessage, LLMResponse, LLMToolCall

T = TypeVar("T", bound=BaseModel)


class AnthropicLLMAdapter(BaseLLMAdapter):
    """Anthropic Claude API adapter supporting tool calling and structured schemas."""

    BASE_URL = "https://api.anthropic.com/v1/messages"

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "claude-3-5-sonnet-20241022",
    ):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.model = model

    def _ensure_api_key(self) -> None:
        if not self.api_key:
            raise FinanceAppException(
                error_code=ErrorCode.AUTH_ERROR,
                message="ANTHROPIC_API_KEY is missing. Configure environment or use MockLLMAdapter for fixture mode.",
            )

    async def complete(
        self,
        messages: list[LLMMessage],
        tools: list[dict[str, Any]] | None = None,
        response_schema: type[T] | None = None,
        trace_context: dict[str, Any] | None = None,
    ) -> LLMResponse:
        self._ensure_api_key()

        # Separate system message from conversation
        system_text = ""
        user_assistant_messages = []
        for m in messages:
            if m.role == "system":
                system_text += f"{m.content}\n"
            else:
                user_assistant_messages.append({"role": m.role, "content": m.content})

        if response_schema is not None:
            # Instruct structured output
            schema_json = json.dumps(response_schema.model_json_schema(), indent=2)
            system_text += (
                f"\nCRITICAL: You must output strictly valid JSON matching this schema:\n{schema_json}\n"
                "Do not include any conversational preamble or markdown code fences."
            )

        payload: dict[str, Any] = {
            "model": self.model,
            "max_tokens": 2048,
            "system": system_text.strip(),
            "messages": user_assistant_messages,
        }
        if tools:
            payload["tools"] = tools

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(self.BASE_URL, headers=headers, json=payload)
            if resp.status_code == 429:
                raise FinanceAppException(
                    error_code=ErrorCode.RATE_LIMITED,
                    message="Anthropic API rate limit reached",
                    retryable=True,
                    retry_after_seconds=30,
                )
            elif resp.status_code != 200:
                raise FinanceAppException(
                    error_code=ErrorCode.PROVIDER_UNAVAILABLE,
                    message=f"Anthropic API error ({resp.status_code}): {resp.text}",
                )
            data = resp.json()

        # Parse text content and tool calls
        raw_text = ""
        tool_calls: list[LLMToolCall] = []
        for block in data.get("content", []):
            if block.get("type") == "text":
                raw_text += block.get("text", "")
            elif block.get("type") == "tool_use":
                tool_calls.append(
                    LLMToolCall(
                        id=block.get("id", ""),
                        tool_name=block.get("name", ""),
                        arguments=block.get("input", {}),
                    )
                )

        usage = data.get("usage", {})
        structured_data = None
        if response_schema is not None and raw_text:
            try:
                # Strip potential markdown fences if present
                clean = raw_text.strip()
                clean = clean.removeprefix("```json")
                clean = clean.removeprefix("```")
                clean = clean.removesuffix("```")
                parsed = json.loads(clean.strip())
                validated = response_schema(**parsed)
                structured_data = validated.model_dump()
            except Exception:
                # Log error or return raw text
                pass

        return LLMResponse(
            content=raw_text,
            tool_calls=tool_calls,
            structured_output=structured_data,
            usage_tokens={
                "prompt_tokens": usage.get("input_tokens", 0),
                "completion_tokens": usage.get("output_tokens", 0),
            },
        )
