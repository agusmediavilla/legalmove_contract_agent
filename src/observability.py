from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Iterator, Optional
import os
import time


@dataclass
class SpanResult:
    output: Any = None
    error: Optional[str] = None
    latency_ms: Optional[int] = None


class NoopSpan:
    def update(self, **kwargs: Any) -> None:
        pass

    def end(self, **kwargs: Any) -> None:
        pass


class LangfuseTracer:
    """Small compatibility wrapper around Langfuse.

    The project must be runnable for reviewers even when Langfuse keys are not configured.
    When LANGFUSE_* variables exist, spans are sent to Langfuse; otherwise the wrapper is a no-op.
    """

    def __init__(self, name: str = "contract-analysis") -> None:
        self.name = name
        self.client = None
        self.root = None
        self.enabled = bool(
            os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY")
        )
        if self.enabled:
            try:
                from langfuse import Langfuse

                self.client = Langfuse(
                    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
                    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
                    host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
                )
                # v2-compatible trace API.
                if hasattr(self.client, "trace"):
                    self.root = self.client.trace(name=name, metadata={"pipeline": name})
            except Exception:
                self.enabled = False
                self.client = None
                self.root = None

    @contextmanager
    def span(self, name: str, input_data: Any = None, metadata: Optional[dict] = None) -> Iterator[Any]:
        start = time.perf_counter()
        span = NoopSpan()
        if self.enabled:
            try:
                parent = self.root if self.root is not None else self.client
                if hasattr(parent, "span"):
                    span = parent.span(name=name, input=input_data, metadata=metadata or {})
            except Exception:
                span = NoopSpan()
        try:
            yield span
            latency_ms = int((time.perf_counter() - start) * 1000)
            try:
                span.update(metadata={**(metadata or {}), "latency_ms": latency_ms})
                span.end()
            except Exception:
                pass
        except Exception as exc:
            latency_ms = int((time.perf_counter() - start) * 1000)
            try:
                span.update(level="ERROR", status_message=str(exc), metadata={"latency_ms": latency_ms})
                span.end()
            except Exception:
                pass
            raise

    def flush(self) -> None:
        if self.enabled and self.client is not None:
            try:
                self.client.flush()
            except Exception:
                pass
