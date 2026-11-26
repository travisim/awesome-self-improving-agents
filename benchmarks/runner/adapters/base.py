"""Abstract interface for memory backends used by the benchmark suite.

An adapter wraps *one* memory backend (Mem0, Zep, Letta, a plain dict, ...) and
exposes the four operations the benchmarks need. Adapters must be pure memory
layers: they do not call an LLM and they do not answer questions. The agent under
test is responsible for turning retrieved context into an answer.

Implementing an adapter is intentionally small so that comparisons are cheap and
reproducible. See `benchmarks/README.md` for the scoring contract.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Type


@dataclass(frozen=True)
class AdapterCapabilities:
    """Declared capabilities, used to explain score deltas rather than to score."""

    vector_search: bool = False
    graph_traversal: bool = False
    temporal_validity: bool = False
    persistence: bool = False
    notes: str = ""


class MemoryAdapter(ABC):
    """Minimal contract every benchmark adapter must satisfy."""

    #: Human-readable identifier shown by `eval_memory.py --list-adapters`.
    name: str = "unnamed-adapter"

    capabilities: AdapterCapabilities = AdapterCapabilities()

    @abstractmethod
    def store(self, key: str, value: str, metadata: Optional[Dict[str, str]] = None) -> None:
        """Persist ``value`` under ``key``.

        ``metadata`` may carry provenance such as ``{"source": "session-1",
        "turn": "12"}``. Implementations should preserve it when they support it.
        """

    @abstractmethod
    def retrieve(self, query: str, limit: int = 5) -> List[str]:
        """Return the most relevant stored values for ``query``, best first.

        Must return values (not internal records) so that scoring is uniform
        across backends.
        """

    @abstractmethod
    def update(self, key: str, new_value: str) -> None:
        """Replace the value for ``key``; required for contradiction tests (COF)."""

    @abstractmethod
    def reset(self) -> None:
        """Clear all state. CSST depends on this to enforce a session boundary."""

    def get(self, key: str) -> Optional[str]:
        """Optional exact-key read. Override if the backend supports it."""
        raise NotImplementedError

    def close(self) -> None:
        """Release connections. Default is a no-op."""


_REGISTRY: Dict[str, Type[MemoryAdapter]] = {}


def register_adapter(cls: Type[MemoryAdapter]) -> Type[MemoryAdapter]:
    """Class decorator that makes an adapter discoverable by the runner."""
    adapter_name = getattr(cls, "name", None)
    if not adapter_name or adapter_name == "unnamed-adapter":
        raise ValueError(f"{cls.__name__} must define a unique `name`")
    if adapter_name in _REGISTRY:
        raise ValueError(f"adapter name already registered: {adapter_name}")
    _REGISTRY[adapter_name] = cls
    return cls


def available_adapters() -> Dict[str, Type[MemoryAdapter]]:
    """Return registered adapters. Empty until a backend is implemented."""
    return dict(_REGISTRY)
