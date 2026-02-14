"""CiteKit client — main entry point for the SDK."""

from __future__ import annotations

import json
from pathlib import Path

from citekit.address import build_address
from citekit.mapper.base import MapperProvider
from citekit.models import Location, Node, ResolvedEvidence, ResourceMap
from citekit.resolvers.audio import AudioResolver
from citekit.resolvers.document import DocumentResolver
from citekit.resolvers.image import ImageResolver
from citekit.resolvers.video import VideoResolver


class CiteKitClient:
    """Main client for ingesting resources, reading maps, and resolving nodes.

    Usage:
        from citekit import CiteKitClient, GeminiMapper

        mapper = GeminiMapper(api_key="YOUR_KEY")
        client = CiteKitClient(mapper=mapper)

        # Ingest a PDF
        resource_map = await client.ingest("textbook.pdf", "document")

        # Later: resolve a specific node
        evidence = client.resolve("textbook", "derivatives.definition")
        print(evidence.output_path)  # → .citekit_output/textbook_pages_12-13.pdf
    """

    def __init__(
        self,
        mapper: MapperProvider | None = None,
        storage_dir: str = ".resource_maps",
        output_dir: str = ".citekit_output",
    ):
        self._mapper = mapper
        self._storage_dir = Path(storage_dir)
        self._output_dir = Path(output_dir)
        self._storage_dir.mkdir(parents=True, exist_ok=True)
        self._output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize resolvers
        self._resolvers = {
            "document": DocumentResolver(output_dir=output_dir),
            "video": VideoResolver(output_dir=output_dir),
            "audio": AudioResolver(output_dir=output_dir),
            "image": ImageResolver(output_dir=output_dir),
        }

    # ── Ingestion ────────────────────────────────────────────────────────────

    async def ingest(
        self,
        resource_path: str,
        resource_type: str,
        resource_id: str | None = None,
    ) -> ResourceMap:
        """Ingest a resource: analyze it with the mapper and save the map locally.

        Args:
            resource_path: Path to the resource file (PDF, video, audio, image).
            resource_type: One of "document", "video", "audio", "image".
            resource_id: Optional custom ID. Defaults to the filename stem.

        Returns:
            The generated ResourceMap.
        """
        if self._mapper is None:
            raise RuntimeError(
                "No mapper provider configured. "
                "Pass a MapperProvider (e.g. GeminiMapper) to CiteKitClient()."
            )

        resource_map = await self._mapper.generate_map(
            resource_path=resource_path,
            resource_type=resource_type,
            resource_id=resource_id,
        )

        # Save to local storage
        self._save_map(resource_map)

        return resource_map

    # ── Map access ───────────────────────────────────────────────────────────

    def get_map(self, resource_id: str) -> ResourceMap:
        """Load a previously generated map from local storage.

        Args:
            resource_id: The resource ID to look up.

        Returns:
            The ResourceMap.

        Raises:
            FileNotFoundError: If no map exists for this resource_id.
        """
        map_path = self._storage_dir / f"{resource_id}.json"
        if not map_path.exists():
            raise FileNotFoundError(
                f"No map found for resource '{resource_id}'. "
                f"Expected at: {map_path}"
            )

        data = json.loads(map_path.read_text(encoding="utf-8"))
        return ResourceMap.model_validate(data)

    def list_maps(self) -> list[str]:
        """List all available resource map IDs."""
        return [
            p.stem
            for p in self._storage_dir.glob("*.json")
        ]

    def get_structure(self, resource_id: str) -> dict:
        """Get the map as a plain dict — useful for MCP/JSON responses."""
        return self.get_map(resource_id).model_dump(mode="json")

    # ── Resolution ───────────────────────────────────────────────────────────

    def resolve(self, resource_id: str, node_id: str) -> ResolvedEvidence:
        """Resolve a node into extracted evidence.

        Args:
            resource_id: The resource to look up.
            node_id: The node ID within that resource.

        Returns:
            ResolvedEvidence with the path to the extracted file.
        """
        resource_map = self.get_map(resource_id)
        node = resource_map.get_node(node_id)

        if node is None:
            available = resource_map.list_node_ids()
            raise ValueError(
                f"Node '{node_id}' not found in resource '{resource_id}'. "
                f"Available nodes: {available}"
            )

        # Pick the right resolver
        modality = node.location.modality
        resolver = self._resolvers.get(modality)

        if resolver is None:
            raise ValueError(f"No resolver for modality: {modality}")

        # Resolve
        output_path = resolver.resolve(node, resource_map.source_path)

        # Build the URI address
        address = build_address(resource_id, node.location)

        return ResolvedEvidence(
            output_path=output_path,
            modality=modality,
            address=address,
            node=node,
            resource_id=resource_id,
        )

    # ── Private ──────────────────────────────────────────────────────────────

    def _save_map(self, resource_map: ResourceMap) -> None:
        """Save a ResourceMap to local JSON storage."""
        map_path = self._storage_dir / f"{resource_map.resource_id}.json"
        data = resource_map.model_dump(mode="json")
        map_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
