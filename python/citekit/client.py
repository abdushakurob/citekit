"""CiteKit client — main entry point for the SDK."""

from __future__ import annotations

import json
import os
from pathlib import Path

from citekit.address import build_address
from citekit.mapper.base import MapperProvider
from citekit.models import Location, Node, ResolvedEvidence, ResourceMap
from citekit.resolvers.audio import AudioResolver
from citekit.resolvers.document import DocumentResolver
from citekit.resolvers.document import DocumentResolver
from citekit.resolvers.image import ImageResolver
from citekit.resolvers.text import TextResolver
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
        base_dir: str = ".",
        storage_dir: str = ".resource_maps",
        output_dir: str = ".citekit_output",
        concurrency_limit: int = 5,
        api_key: str | None = None,
        model: str = "gemini-2.0-flash",
        max_retries: int = 3,
    ):
        self._mapper = mapper
        if self._mapper is None and (api_key or os.environ.get("GEMINI_API_KEY")):
            from citekit.mapper.gemini import GeminiMapper
            key = api_key or os.environ.get("GEMINI_API_KEY")
            self._mapper = GeminiMapper(api_key=key, model=model, max_retries=max_retries)

        base_path = Path(base_dir)
        self._storage_dir = base_path / storage_dir
        self._output_dir = base_path / output_dir
        self._storage_dir.mkdir(parents=True, exist_ok=True)
        self._output_dir.mkdir(parents=True, exist_ok=True)
        
        # Concurrency control
        import asyncio
        self._semaphore = asyncio.Semaphore(concurrency_limit)

        # Initialize resolvers
        self._resolvers = {
            "document": DocumentResolver(output_dir=str(self._output_dir)),
            "video": VideoResolver(output_dir=str(self._output_dir)),
            "audio": AudioResolver(output_dir=str(self._output_dir)),
            "image": ImageResolver(output_dir=str(self._output_dir)),
            "text": TextResolver(output_dir=str(self._output_dir)),
        }

    # ── Ingestion ────────────────────────────────────────────────────────────

    async def ingest(
        self,
        resource_path: str,
        resource_type: str,
        resource_id: str | None = None,
    ) -> ResourceMap:
        """Ingest a resource: analyze it with the mapper and save the map locally.
        
        Features:
        - Calculates SHA-256 hash of the file.
        - Checks local cache for existing map with same hash.
        - Limits concurrent mapper calls using a semaphore.

        Args:
            resource_path: Path to the resource file (PDF, video, audio, image, text).
            resource_type: One of "document", "video", "audio", "image", "text".
            resource_id: Optional custom ID. Defaults to the filename stem.

        Returns:
            The generated ResourceMap.
        """
        if self._mapper is None:
            raise RuntimeError(
                "No mapper provider configured. "
                "Pass a MapperProvider (e.g. GeminiMapper) to CiteKitClient()."
            )

        path_obj = Path(resource_path)
        if not path_obj.exists():
            raise FileNotFoundError(f"File not found: {resource_path}")

        # 1. Hashing & Caching
        file_hash = self._calculate_file_hash(path_obj)
        
        # Check if we already have a map for this content hash
        # We scan existing maps (simple linear scan is fine for local typical usage)
        cached_map = self._find_map_by_hash(file_hash)
        if cached_map:
            # If user provided a specific ID, verify it matches or just warn?
            # For simplicity, if content is identical, we return the existing map 
            # BUT we must ensure the returned map has the requested ID if provided.
            # If IDs differ, we might need to copy/alias.
            # For now: return the cached one. 
            print(f"DEBUG: Cache hit for {path_obj.name} (Hash: {file_hash[:8]}...)")
            return cached_map

        # Determine ID if not provided
        if resource_id is None:
            resource_id = path_obj.stem

        # 2. Queueing / Concurrency Control
        async with self._semaphore:
            resource_map = await self._mapper.generate_map(
                resource_path=resource_path,
                resource_type=resource_type,
                resource_id=resource_id,
            )

        # Inject hash into metadata (we need to update the model to support it or just add to dict)
        # Assuming ResourceMap.metadata is a dict or supports extra fields
        if resource_map.metadata is None:
            resource_map.metadata = {}
        resource_map.metadata["source_hash"] = file_hash
        resource_map.metadata["source_size"] = path_obj.stat().st_size

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

    def resolve(self, resource_id: str, node_id: str, virtual: bool = False) -> ResolvedEvidence:
        """Resolve a node into extracted evidence.

        Args:
            resource_id: The resource to look up.
            node_id: The node ID within that resource.
            virtual: If True, returns only metadata without physical extraction.

        Returns:
            ResolvedEvidence with the path to the extracted file (or None if virtual).
        """
        resource_map = self.get_map(resource_id)
        node = resource_map.get_node(node_id)

        if node is None:
            available = resource_map.list_node_ids()
            raise ValueError(
                f"Node '{node_id}' not found in resource '{resource_id}'. "
                f"Available nodes: {available}"
            )

        # Build the URI address
        address = build_address(resource_id, node.location)
        modality = node.location.modality

        # 1. Virtual Resolution: Early Return
        if virtual:
            return ResolvedEvidence(
                output_path=None,
                modality=modality,
                address=address,
                node=node,
                resource_id=resource_id,
            )

        # 2. Physical Resolution
        resolver = self._resolvers.get(modality)
        if resolver is None:
            raise ValueError(f"No resolver for modality: {modality}")

        output_path = resolver.resolve(node, resource_map.source_path)

        return ResolvedEvidence(
            output_path=output_path,
            modality=modality,
            address=address,
            node=node,
            resource_id=resource_id,
        )

    # ── Private ──────────────────────────────────────────────────────────────

    def _calculate_file_hash(self, path: Path) -> str:
        """Calculate SHA-256 hash of a file."""
        import hashlib
        sha256_hash = hashlib.sha256()
        with open(path, "rb") as f:
            # Read and update hash string value in blocks of 4K
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def _find_map_by_hash(self, file_hash: str) -> ResourceMap | None:
        """Find an existing map that matches the file hash."""
        for map_file in self._storage_dir.glob("*.json"):
            try:
                data = json.loads(map_file.read_text(encoding="utf-8"))
                # Check metadata for source_hash
                meta = data.get("metadata", {})
                if meta.get("source_hash") == file_hash:
                    return ResourceMap.model_validate(data)
            except Exception:
                continue
        return None

    def _save_map(self, resource_map: ResourceMap) -> None:
        """Save a ResourceMap to local JSON storage."""
        map_path = self._storage_dir / f"{resource_map.resource_id}.json"
        data = resource_map.model_dump(mode="json")
        map_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
