"""Structured JSON logging with sensitive data redaction."""

import json
import logging
import re
from datetime import UTC, datetime
from typing import Any

SENSITIVE_PATTERNS = [
    re.compile(r"api[-_]?key", re.IGNORECASE),
    re.compile(r"token", re.IGNORECASE),
    re.compile(r"secret", re.IGNORECASE),
    re.compile(r"password", re.IGNORECASE),
    re.compile(r"bearer\s+[a-zA-Z0-9_\-\.]+", re.IGNORECASE),
]


def redact_sensitive(obj: Any) -> Any:
    """Recursively redact API keys and secrets from logs and traces."""
    if isinstance(obj, dict):
        clean = {}
        for k, v in obj.items():
            if any(p.search(str(k)) for p in SENSITIVE_PATTERNS):
                clean[k] = "[REDACTED]"
            else:
                clean[k] = redact_sensitive(v)
        return clean
    elif isinstance(obj, list):
        return [redact_sensitive(i) for i in obj]
    elif isinstance(obj, str):
        for p in SENSITIVE_PATTERNS:
            if "bearer" in p.pattern.lower():
                obj = p.sub("Bearer [REDACTED]", obj)
        return obj
    return obj


class StructuredJsonFormatter(logging.Formatter):
    """Formats log records as single-line JSON with standardized fields."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Extra context attributes
        for key in (
            "run_id",
            "trace_id",
            "agent",
            "workflow_state",
            "tool",
            "provider",
            "symbol",
            "duration_ms",
            "error_code",
        ):
            if hasattr(record, key):
                log_obj[key] = getattr(record, key)

        redacted = redact_sensitive(log_obj)
        return json.dumps(redacted, default=str)


def get_logger(name: str) -> logging.Logger:
    """Get a structured logger with JSON formatting."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(StructuredJsonFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
