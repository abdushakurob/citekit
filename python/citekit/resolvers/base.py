"""Abstract base class for resolvers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from citekit.models import Node


class Resolver(ABC):
    """Base class for all resolvers.

    A resolver takes a node and source file, and extracts the physical
    evidence (pages, clip, crop, etc.) into an output file.
    """

    def __init__(self, output_dir: str = ".citekit_output"):
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def resolve(self, node: Node, source_path: str) -> str:
        """Extract evidence for a node from the source file.

        Args:
            node: The node to resolve, containing location info.
            source_path: Path to the original resource file.

        Returns:
            Path to the generated output file.
        """
        ...
