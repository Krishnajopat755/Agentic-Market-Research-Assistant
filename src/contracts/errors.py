"""Typed error codes and custom exceptions for the Agentic Market Research Assistant."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ErrorCode(str, Enum):
    AUTH_ERROR = "AUTH_ERROR"
    RATE_LIMITED = "RATE_LIMITED"
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"
    PROVIDER_SCHEMA_CHANGED = "PROVIDER_SCHEMA_CHANGED"
    INVALID_SYMBOL = "INVALID_SYMBOL"
    EMPTY_RESULT = "EMPTY_RESULT"
    STALE_DATA = "STALE_DATA"
    INVALID_TIME_RANGE = "INVALID_TIME_RANGE"
    POINT_IN_TIME_VIOLATION = "POINT_IN_TIME_VIOLATION"
    TOOL_NOT_AUTHORIZED = "TOOL_NOT_AUTHORIZED"
    STATE_PRECONDITION_FAILED = "STATE_PRECONDITION_FAILED"
    ARTIFACT_INTEGRITY_FAILED = "ARTIFACT_INTEGRITY_FAILED"
    EVIDENCE_VALIDATION_FAILED = "EVIDENCE_VALIDATION_FAILED"


class ErrorEnvelope(BaseModel):
    """Standardized error contract matching doc 05."""

    error_code: ErrorCode
    message: str
    retryable: bool = False
    retry_after_seconds: int | None = None
    trace_id: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class FinanceAppException(Exception):
    """Base exception carrying structured ErrorEnvelope."""

    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        retryable: bool = False,
        retry_after_seconds: int | None = None,
        trace_id: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.envelope = ErrorEnvelope(
            error_code=error_code,
            message=message,
            retryable=retryable,
            retry_after_seconds=retry_after_seconds,
            trace_id=trace_id,
            details=details or {},
        )

    def to_dict(self) -> dict[str, Any]:
        return self.envelope.model_dump()
