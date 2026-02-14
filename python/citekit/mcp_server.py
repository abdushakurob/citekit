"""CiteKit MCP Server — exposes getStructure and resolve tools.

Run with:
    python -m citekit.mcp_server

Or programmatically:
    from citekit.mcp_server import create_server
    server = create_server()
"""

from __future__ import annotations

import json
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from citekit.client import CiteKitClient


def create_server(
    storage_dir: str = ".resource_maps",
    output_dir: str = ".citekit_output",
) -> Server:
    """Create an MCP server with CiteKit tools.

    Args:
        storage_dir: Directory where resource maps are stored.
        output_dir: Directory for resolved output files.
    """
    server = Server("citekit")
    client = CiteKitClient(storage_dir=storage_dir, output_dir=output_dir)

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="listResources",
                description="List all available resource map IDs that have been ingested.",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            Tool(
                name="getStructure",
                description=(
                    "Get the structured map of a resource. "
                    "Returns a JSON map with nodes, each pointing to a concept/section "
                    "and its physical location (pages, timestamps, regions). "
                    "Read the map to decide which node to resolve."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "resource_id": {
                            "type": "string",
                            "description": "The resource ID to get the structure for.",
                        },
                    },
                    "required": ["resource_id"],
                },
            ),
            Tool(
                name="resolve",
                description=(
                    "Resolve a specific node from a resource map into extracted evidence. "
                    "For documents, this produces a mini-PDF with only the relevant pages. "
                    "For video/audio, this produces a clip of the relevant time segment. "
                    "For images, this produces a cropped region."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "resource_id": {
                            "type": "string",
                            "description": "The resource ID.",
                        },
                        "node_id": {
                            "type": "string",
                            "description": "The node ID to resolve (e.g. 'derivatives.definition').",
                        },
                    },
                    "required": ["resource_id", "node_id"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        if name == "listResources":
            resource_ids = client.list_maps()
            return [TextContent(
                type="text",
                text=json.dumps({"resources": resource_ids}, indent=2),
            )]

        elif name == "getStructure":
            resource_id = arguments["resource_id"]
            try:
                structure = client.get_structure(resource_id)
                return [TextContent(
                    type="text",
                    text=json.dumps(structure, indent=2),
                )]
            except FileNotFoundError as e:
                return [TextContent(type="text", text=f"Error: {e}")]

        elif name == "resolve":
            resource_id = arguments["resource_id"]
            node_id = arguments["node_id"]
            try:
                evidence = client.resolve(resource_id, node_id)
                return [TextContent(
                    type="text",
                    text=json.dumps(evidence.model_dump(mode="json"), indent=2),
                )]
            except (FileNotFoundError, ValueError) as e:
                return [TextContent(type="text", text=f"Error: {e}")]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    return server


async def main():
    """Run the CiteKit MCP server over stdio."""
    server = create_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
