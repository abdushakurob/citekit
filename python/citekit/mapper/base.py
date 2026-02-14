"""Abstract base class for mapper providers."""

from __future__ import annotations

from abc import ABC, abstractmethod

from citekit.models import ResourceMap


class MapperProvider(ABC):
    """Base class for all mapper providers.

    A mapper analyzes a resource file and produces a structured ResourceMap
    containing nodes that point to physical locations within the resource.

    To create a custom provider, subclass this and implement generate_map().
    """

    @abstractmethod
    async def generate_map(
        self,
        resource_path: str,
        resource_type: str,
        resource_id: str | None = None,
    ) -> ResourceMap:
        """Analyze a resource and produce a structured map.

        Args:
            resource_path: Path to the resource file.
            resource_type: Type of resource ("document", "video", "audio", "image").
            resource_id: Optional custom ID. If not provided, derived from filename.

        Returns:
            A ResourceMap with nodes pointing to locations in the resource.
        """
        ...
