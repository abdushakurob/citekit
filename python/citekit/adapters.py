from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import json
from pathlib import Path
from .models import ResourceMap, Node, Location, ResourceType

class MapAdapter(ABC):
    """
    Abstract base class for all Map Adapters.
    
    A Map Adapter converts an external data source (file, API response, object)
    into a standardized CiteKit ResourceMap.
    """
    
    @abstractmethod
    def adapt(self, input_data: Any, **kwargs) -> ResourceMap:
        """
        Convert input_data into a ResourceMap.
        
        Args:
            input_data: The raw input to adapt (e.g., file path, dict, graph object).
            **kwargs: Additional arguments specific to the adapter.
            
        Returns:
            A valid ResourceMap object.
        """
        pass

class GenericAdapter(MapAdapter):
    """
    A simple pass-through adapter that validates a dict or JSON file 
    against the ResourceMap schema.
    """
    def adapt(self, input_data: Any, **kwargs) -> ResourceMap:
        if isinstance(input_data, str) or isinstance(input_data, Path):
            data = json.loads(Path(input_data).read_text(encoding="utf-8"))
        elif isinstance(input_data, dict):
            data = input_data
        else:
            raise ValueError("GenericAdapter expects a file path or a dictionary.")
            
        return ResourceMap(**data)

class GraphRAGAdapter(MapAdapter):
    """
    Adapter for Microsoft GraphRAG artifacts (specifically entity/community reports).
    
    This is a heuristic adapter that attempts to map GraphRAG concepts to CiteKit:
    - Entities/Communities -> Nodes
    - Descriptions -> Summaries
    - Source chunks -> Locations (Virtual)
    """
    
    def adapt(self, input_data: Any, **kwargs) -> ResourceMap:
        """
        Expects a GraphRAG output file (JSON) containing a list of entities or communities.
        """
        if isinstance(input_data, str) or isinstance(input_data, Path):
            content = Path(input_data).read_text(encoding="utf-8")
            data = json.loads(content)
        elif isinstance(input_data, list):
            data = input_data
        else:
             raise ValueError("GraphRAGAdapter expects a JSON file path or a list of objects.")

        # Heuristic: Check if it's a list of entities or communities
        nodes = []
        resource_title = kwargs.get("title", "GraphRAG Import")
        
        for item in data:
            # Handle GraphRAG Entity
            if "name" in item and "description" in item:
                # Basic Entity
                nodes.append(Node(
                    id=self._sanitize_id(item["name"]),
                    title=item["name"],
                    type="entity",
                    summary=item["description"],
                    location=Location(modality="virtual", virtual_address=f"graph://{item.get('id', item['name'])}")
                ))
            elif "title" in item and "summary" in item:
                 # Community Report
                nodes.append(Node(
                    id=f"community_{item.get('id', 'unknown')}",
                    title=item["title"],
                    type="community",
                    summary=item["summary"],
                    location=Location(modality="virtual", virtual_address=f"graph://community/{item.get('id')}")
                ))

        if not nodes:
            raise ValueError("Could not parse valid GraphRAG entities or communities from input.")

        return ResourceMap(
            resource_id=kwargs.get("resource_id", "graphrag_import"),
            type="virtual",
            title=resource_title,
            source_path=str(input_data) if isinstance(input_data, (str, Path)) else "virtual",
            nodes=nodes
        )

    def _sanitize_id(self, name: str) -> str:
        return "".join(c if c.isalnum() else "_" for c in name).lower()

class LlamaIndexAdapter(MapAdapter):
    """
    Adapter for LlamaIndex Node objects or JSON exports.
    """
    def adapt(self, input_data: Any, **kwargs) -> ResourceMap:
        """
        Accepts a dict (from to_dict()) or a list of dicts/Nodes.
        """
        # Load from file if string
        if isinstance(input_data, (str, Path)):
             data = json.loads(Path(input_data).read_text(encoding="utf-8"))
        else:
             data = input_data
             
        # Normalize to list of nodes
        raw_nodes = []
        if isinstance(data, dict):
            # Might be a whole index dict, try to find nodes
            if "nodes" in data:
                raw_nodes = data["nodes"]
            else:
                 # Assume single node dict
                 raw_nodes = [data]
        elif isinstance(data, list):
            raw_nodes = data
            
        nodes = []
        for item in raw_nodes:
            # LlamaIndex nodes usually have 'id_', 'text', 'metadata'
            # We map: id_ -> id, text -> summary/title, metadata -> metadata
            
            # Handle standard LlamaIndex serialization
            node_id = item.get("id_", item.get("node_id", "unknown"))
            text = item.get("text", "")
            meta = item.get("metadata", {})
            
            # Try to determine useful title
            title = meta.get("file_name", meta.get("title", f"Node {node_id[:8]}"))
            
            # Determine location
            # LlamaIndex often has start_char/end_char
            loc = Location(modality="text", lines=(0, 0))
            if "start_char_idx" in item and "end_char_idx" in item:
                # We don't have direct char-to-line mapping without the file, 
                # but we can store it in metadata or try to approximate if source is available.
                # For now, we use the virtual/text modality.
                loc = Location(modality="text", lines=(0, 0)) # Placeholder
            
            nodes.append(Node(
                id=node_id,
                title=title,
                type="text_chunk",
                summary=text[:200] + "..." if len(text) > 200 else text,
                location=loc,
                children=[]
            ))
            
        if not nodes:
             raise ValueError("No valid LlamaIndex nodes found.")

        return ResourceMap(
            resource_id=kwargs.get("resource_id", "llamaindex_import"),
            type="document",
            title=kwargs.get("title", "LlamaIndex Import"),
            source_path="virtual",  # LlamaIndex usually references external files
            nodes=nodes
        )
