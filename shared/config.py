"""Bridge module — re-exports settings from core.config for new sub-packages."""
from core.config import settings  # noqa: F401

__all__ = ["settings"]
