"""OpenTelemetry-compatible distributed tracing wrapper."""

import time
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any
from uuid import uuid4

from src.observability.logging import get_logger, redact_sensitive

logger = get_logger("tracing")


class Span:
    """Represents a trace span with attributes and timing."""

    def __init__(
        self, name: str, trace_id: str, span_id: str, attributes: dict[str, Any] | None = None
    ):
        self.name = name
        self.trace_id = trace_id
        self.span_id = span_id
        self.attributes = attributes or {}
        self.start_time = time.perf_counter()
        self.end_time: float | None = None
        self.duration_ms: float = 0.0
        self.status = "OK"
        self.error: str | None = None

    def set_attribute(self, key: str, value: Any) -> None:
        self.attributes[key] = value

    def finish(self, status: str = "OK", error: str | None = None) -> None:
        self.end_time = time.perf_counter()
        self.duration_ms = round((self.end_time - self.start_time) * 1000.0, 2)
        self.status = status
        self.error = error


class Tracer:
    """Lightweight in-process tracer compatible with OpenTelemetry semantic conventions."""

    def __init__(self, service_name: str = "agentic_market_research"):
        self.service_name = service_name
        self.completed_spans: list[Span] = []

    @contextmanager
    def start_span(
        self,
        name: str,
        trace_id: str | None = None,
        attributes: dict[str, Any] | None = None,
    ) -> Generator[Span]:
        tid = trace_id or uuid4().hex
        sid = uuid4().hex[:16]
        span = Span(name=name, trace_id=tid, span_id=sid, attributes=attributes or {})
        try:
            yield span
            span.finish(status="OK")
        except Exception as e:
            span.finish(status="ERROR", error=str(e))
            raise
        finally:
            self.completed_spans.append(span)
            clean_attrs = redact_sensitive(span.attributes)
            logger.info(
                f"Span completed: {name} in {span.duration_ms}ms [{span.status}]",
                extra={
                    "trace_id": span.trace_id,
                    "tool": name,
                    "duration_ms": span.duration_ms,
                    **clean_attrs,
                },
            )


default_tracer = Tracer()
