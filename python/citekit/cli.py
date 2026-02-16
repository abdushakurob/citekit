import asyncio
import functools
import json
import os
import sys
from pathlib import Path

import click
from citekit.client import CiteKitClient

def async_command(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapper

@click.group()
def main():
    """CiteKit CLI - Local AI Resource Mapper & Resolver."""
    pass

@main.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--type", "-t", help="Resource type (document, video, audio, image). If omitted, inferred from extension.")
@click.option("--concurrency", "-c", default=5, help="Max parallel mapper calls.")
@click.option("--retries", "-r", default=3, help="Max retries for API failures.")
@async_command
async def ingest(path, type, concurrency, retries):
    """Ingest a file and generate a resource map."""
    client = CiteKitClient(concurrency_limit=concurrency, max_retries=retries)
    
    if not type:
        ext = Path(path).suffix.lower()
        if ext in (".pdf", ".txt", ".md"):
            type = "document"
        elif ext in (".mp4", ".mov", ".avi", ".mkv"):
            type = "video"
        elif ext in (".mp3", ".wav", ".m4a"):
            type = "audio"
        elif ext in (".png", ".jpg", ".jpeg", ".webp"):
            type = "image"
        else:
            click.echo(f"⚠️ Could not infer type from extension '{ext}'. Please specify --type.", err=True)
            sys.exit(1)

    click.echo(f"🔍 Ingesting {path} as '{type}'...")
    try:
        resource_map = await client.ingest(path, resource_type=type)
        click.echo(f"✅ Map generated: {resource_map.resource_id}")
        click.echo(f"   Title: {resource_map.title}")
        click.echo(f"   Nodes: {len(resource_map.nodes)}")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@main.command()
@click.argument("node_id")
@click.option("--resource", "-res", help="Resource ID (optional if node_id is unique).")
@click.option("--virtual", is_flag=True, help="Virtual resolution (metadata only).")
@async_command
async def resolve(node_id, resource, virtual):
    """Resolve a node ID to its value (file chunk)."""
    client = CiteKitClient()
    
    click.echo(f"📎 Resolving node: {node_id}")
    try:
        # We need to support the case where node_id is a full address or separate
        if "." in node_id and not resource:
            rid, nid = node_id.split(".", 1)
        else:
            rid, nid = resource, node_id

        if not rid:
            # Try to find which resource contains this node
            click.echo("⚠️ Resource ID missing. Use --resource or rid.nid format.")
            sys.exit(1)

        evidence = await client.resolve(rid, nid, virtual=virtual)
        if virtual:
            click.echo("✅ Virtual resolution successful.")
        else:
            click.echo(f"✅ Output: {evidence.output_path}")
        click.echo(f"   Modality: {evidence.modality}")
        click.echo(f"   Address: {evidence.address}")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@main.command()
@click.argument("resource_id")
@async_command
async def structure(resource_id):
    """Get the JSON structure (map) for a resource ID."""
    client = CiteKitClient()
    
    try:
        resource_map = client.get_map(resource_id)
        click.echo(json.dumps(resource_map.model_dump(), indent=2, default=str))
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@main.command("list")
@click.argument("resource_id", required=False)
@async_command
async def list_resources(resource_id):
    """List ingested resources or nodes within a resource."""
    client = CiteKitClient()
    
    if resource_id:
        # List nodes for a specific resource
        try:
            resource_map = client.get_map(resource_id)
            click.echo(f"🔍 Nodes in '{resource_id}':")
            # Flatten nodes for display if needed, but for now just top-level
            for node in resource_map.nodes:
                click.echo(f" - {node.id} ({node.type}): {node.title}")
                if node.children:
                    for child in node.children:
                        click.echo(f"   └─ {child.id} ({child.type}): {child.title}")
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            sys.exit(1)
        return

    # List all resources
    map_dir = Path(".resource_maps")
    if not map_dir.exists():
        click.echo("No resources found (directory .resource_maps missing).")
        return

    maps = list(map_dir.glob("*.json"))
    if not maps:
        click.echo("No resources found.")
        return

    click.echo(f"found {len(maps)} resources:")
    for map_file in maps:
        try:
            data = json.loads(map_file.read_text(encoding="utf-8"))
            click.echo(f" - {data.get('resource_id')} ({data.get('type')}): {data.get('title')}")
        except:
            click.echo(f" - {map_file.name} (corrupt)")

@main.command()
@async_command
async def serve():
    """Run the MCP server (stdio mode) for AI agents."""
    from citekit.mcp_server import create_server
    from mcp.server.stdio import stdio_server

    server = create_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

@main.command()
@click.argument("node_id")
@click.option("--resource", "-res", help="Resource ID (optional if node_id is unique).")
@async_command
async def inspect(node_id, resource):
    """Inspect a node's metadata without resolving details."""
    client = CiteKitClient()
    
    # Logic to find resource/node similar to resolve
    if "." in node_id and not resource:
        rid, nid = node_id.split(".", 1)
    else:
        rid, nid = resource, node_id

    if not rid:
        click.echo("⚠️ Resource ID missing. Use --resource or rid.nid format.")
        sys.exit(1)

    try:
        # We don't have a direct get_node method, so we read the map
        resource_map = client.get_map(rid)
        
        # Recursive search for node
        def find_node(nodes, target_id):
            for node in nodes:
                if node.id == target_id:
                    return node
                if node.children:
                    found = find_node(node.children, target_id)
                    if found:
                        return found
            return None

        node = find_node(resource_map.nodes, nid)
        if not node:
            click.echo(f"❌ Node '{nid}' not found in resource '{rid}'.")
            sys.exit(1)
            
        click.echo(f"🔍 Node: {node.id}")
        click.echo(f"   Resource: {rid} ({resource_map.type})")
        click.echo(f"   Title: {node.title}")
        click.echo(f"   Type: {node.type}")
        click.echo(f"   Location: {node.location}")
        if node.summary:
            click.echo(f"   Summary: {node.summary}")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
