"""Utilities for aggregating multiple resource maps into agent-friendly context."""

from __future__ import annotations
from typing import List
from citekit.models import ResourceMap

def create_agent_context(maps: List[ResourceMap], format: str = "markdown") -> str:
    """Aggregates multiple ResourceMaps into a single string for LLM context.
    
    Args:
        maps: List of ResourceMap objects.
        format: Output format ('markdown' or 'json').
        
    Returns:
        A string containing the aggregated content structure.
    """
    if format == "json":
        # Return a compact JSON representation
        summary = []
        for rmap in maps:
            summary.append({
                "id": rmap.resource_id,
                "title": rmap.title,
                "type": rmap.type,
                "nodes": [
                    {"id": node.id, "title": node.title, "summary": node.summary}
                    for node in rmap.nodes
                ]
            })
        import json
        return json.dumps(summary, indent=2)
    
    # Default: Markdown
    lines = ["# Available Resources Index", ""]
    for rmap in maps:
        lines.append(f"## {rmap.title} (ID: {rmap.resource_id}, Type: {rmap.type})")
        for node in rmap.nodes:
            lines.append(f"- **{node.id}**: {node.title} - {node.summary or ''}")
        lines.append("")
        
    return "\n".join(lines).strip()
