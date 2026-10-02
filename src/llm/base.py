"""LLM Provider abstraction matching Section 5 of System Architecture."""

from abc import ABC, abstractmethod
from typing import Any, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T", bound=BaseModel)


class LLMMessage(BaseModel):
    role: str  # system, user, assistant
    content: str


class LLMToolCall(BaseModel):
    id: str
    tool_name: str
    arguments: dict[str, Any]


class LLMResponse(BaseModel):
    content: str | None = None
    tool_calls: list[LLMToolCall] = Field(default_factory=list)
    structured_output: dict[str, Any] | None = None
    usage_tokens: dict[str, int] = Field(default_factory=dict)
    finish_reason: str = "stop"


class BaseLLMAdapter(ABC):
    """Abstract interface for LLM calls."""

    @abstractmethod
    async def complete(
        self,
        messages: list[LLMMessage],
        tools: list[dict[str, Any]] | None = None,
        response_schema: type[T] | None = None,
        trace_context: dict[str, Any] | None = None,
    ) -> LLMResponse:
        """Execute model completion with optional tool schema and structured output validation."""
