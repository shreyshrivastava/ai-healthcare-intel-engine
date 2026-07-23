from __future__ import annotations

import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from threading import Lock

logger = logging.getLogger(__name__)


@dataclass
class MetricsStore:
    request_count: int = 0
    error_count: int = 0
    total_latency_ms: float = 0.0
    latencies_ms: deque[float] = field(default_factory=lambda: deque(maxlen=200))
    paths: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    lock: Lock = field(default_factory=Lock)

    def record(self, method: str, path: str, status_code: int, duration_ms: float) -> None:
        with self.lock:
            self.request_count += 1
            self.total_latency_ms += duration_ms
            self.latencies_ms.append(duration_ms)
            self.paths[f"{method} {path}"] += 1
            if status_code >= 500:
                self.error_count += 1

    def snapshot(self) -> dict:
        with self.lock:
            average_ms = self.total_latency_ms / self.request_count if self.request_count else 0.0
            recent = list(self.latencies_ms)
            recent_sorted = sorted(recent)
            median_ms = recent_sorted[len(recent_sorted) // 2] if recent_sorted else 0.0
            return {
                "request_count": self.request_count,
                "error_count": self.error_count,
                "average_latency_ms": round(average_ms, 3),
                "recent_median_latency_ms": round(median_ms, 3),
                "paths": dict(sorted(self.paths.items())),
            }


metrics_store = MetricsStore()


def record_request(method: str, path: str, status_code: int, duration_ms: float) -> None:
    metrics_store.record(method, path, status_code, duration_ms)
    logger.info(
        "request_complete method=%s path=%s status=%s duration_ms=%.3f",
        method,
        path,
        status_code,
        duration_ms,
    )


def metrics_snapshot() -> dict:
    return metrics_store.snapshot()


def perf_counter_ms() -> float:
    return time.perf_counter() * 1000
