"""Memory backend adapters for the self-improvement benchmark suite.

Importing this package exposes `MemoryAdapter` and the registry helpers. Concrete
backends live in sibling modules and register themselves with `@register_adapter`.
"""

from .base import (  # noqa: F401
    AdapterCapabilities,
    MemoryAdapter,
    available_adapters,
    register_adapter,
)

__all__ = [
    "AdapterCapabilities",
    "MemoryAdapter",
    "available_adapters",
    "register_adapter",
]
