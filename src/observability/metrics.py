"""Operational metrics collector."""

from collections import defaultdict
from typing import Any


class MetricsCollector:
    """Collects counters, latencies, and operational stats matching doc 10."""

    def __init__(self):
        self.counters = defaultdict(int)
        self.latencies = defaultdict(list)

    def inc_counter(self, name: str, value: int = 1) -> None:
        self.counters[name] += value

    def record_latency(self, name: str, latency_ms: float) -> None:
        self.latencies[name].append(latency_ms)

    def snapshot(self) -> dict[str, Any]:
        stats = {"counters": dict(self.counters), "latencies": {}}
        for k, v in self.latencies.items():
            if v:
                stats["latencies"][k] = {
                    "count": len(v),
                    "mean_ms": round(sum(v) / len(v), 2),
                    "max_ms": round(max(v), 2),
                }
        return stats


default_metrics = MetricsCollector()
