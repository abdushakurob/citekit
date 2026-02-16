"""Core data models for CiteKit."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


class Location(BaseModel):
    """Physical location within a resource that a node points to."""

    modality: Literal["document", "video", "audio", "image", "text"]

    # Document-specific
    pages: list[int] | None = None

    # Text-specific
    lines: tuple[int, int] | None = None

    # Video/Audio-specific (seconds)
    start: float | None = None
    end: float | None = None

    # Image-specific (normalized 0-1 bounding box)
    bbox: tuple[float, float, float, float] | None = None


class Node(BaseModel):
    """A concept or section within a resource, pointing to a physical location."""

    id: str = Field(..., description="Dot-separated identifier, e.g. 'derivatives.definition'")
    title: str | None = None
    type: str = Field(..., description="Node type: definition, example, explanation, diagram, etc.")
    location: Location
    summary: str | None = None
    children: list[Node] = Field(default_factory=list)


class ResourceMap(BaseModel):
    """Structured map of a resource — the first output of ingestion."""

    resource_id: str
    type: Literal["document", "video", "audio", "image", "text"]
    title: str
    source_path: str
    metadata: dict[str, str | int | float | None] | None = None
    nodes: list[Node] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def get_node(self, node_id: str) -> Node | None:
        """Find a node by its ID."""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    def list_node_ids(self) -> list[str]:
        """Return all node IDs in this map."""
        return [node.id for node in self.nodes]


class ResolvedEvidence(BaseModel):
    """Result of resolving a node — the extracted evidence."""

    output_path: str | None = Field(None, description="Path to the extracted file (mini-PDF, clip, crop, etc.). Optional for virtual resolution.")
    modality: str
    address: str = Field(..., description="URI-style address, e.g. doc://book#pages=12-13")
    node: Node
    resource_id: str
