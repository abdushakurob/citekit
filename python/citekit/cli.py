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
@click.option("--type", "-t", help="Resource type (document, video, audio, image, text). If omitted, inferred from extension.")
@click.option("--concurrency", "-c", default=5, help="Max parallel mapper calls.")
@click.option("--retries", "-r", default=3, help="Max retries for API failures.")
@click.option("--mapper", "-m", help="Mapper name ('gemini') or path to a .py file exporting a custom mapper.")
@click.option("--mapper-config", help="JSON string of kwargs for custom mapper initialization.")
@async_command
async def ingest(path, type, concurrency, retries, mapper, mapper_config):
    """Ingest a file and generate a resource map."""
    mapper_instance = None
    if mapper and mapper != "gemini":
        import importlib.util
        if not mapper.endswith(".py"):
            click.echo("[ERROR] --mapper must be 'gemini' or a path to a .py file.", err=True)
            sys.exit(1)

        spec = importlib.util.spec_from_file_location("custom_mapper", mapper)
        if not spec or not spec.loader:
            click.echo(f"[ERROR] Could not load custom mapper from {mapper}", err=True)
            sys.exit(1)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        config = {}
        if mapper_config:
            try:
                config = json.loads(mapper_config)
            except json.JSONDecodeError as e:
                click.echo(f"[ERROR] Invalid --mapper-config JSON: {e}", err=True)
                sys.exit(1)

        if hasattr(module, "Mapper"):
            mapper_instance = module.Mapper(**config)
        elif hasattr(module, "create_mapper") and callable(module.create_mapper):
            mapper_instance = module.create_mapper(**config)
        elif hasattr(module, "mapper"):
            mapper_instance = module.mapper
        else:
            click.echo("[ERROR] Custom mapper must export a Mapper class, create_mapper() factory, or mapper instance.", err=True)
            sys.exit(1)

    client = CiteKitClient(
        mapper=mapper_instance,
        concurrency_limit=concurrency,
        max_retries=retries,
    )
    
    if not type:
        ext = Path(path).suffix.lower()
        if ext in (".pdf",):
            type = "document"
        elif ext in (".txt", ".md", ".py", ".js", ".ts", ".json", ".yaml", ".yml", ".rst"):
            type = "text"
        elif ext in (".mp4", ".mov", ".avi", ".mkv"):
            type = "video"
        elif ext in (".mp3", ".wav", ".m4a"):
            type = "audio"
        elif ext in (".png", ".jpg", ".jpeg", ".webp"):
            type = "image"
        else:
            click.echo(f"[!] Could not infer type from extension '{ext}'. Please specify --type.", err=True)
            sys.exit(1)

    click.echo(f"[INFO] Ingesting {path} as '{type}'...")
    try:
        resource_map = await client.ingest(path, resource_type=type)
        click.echo(f"[SUCCESS] Map generated: {resource_map.resource_id}")
        click.echo(f"   Title: {resource_map.title}")
        click.echo(f"   Nodes: {len(resource_map.nodes)}")
    except Exception as e:
        click.echo(f"[ERROR] {e}", err=True)
        sys.exit(1)

@main.command()
@click.argument("node_id")
@click.option("--resource", "-res", help="Resource ID (optional if node_id is unique).")
@click.option("--virtual", is_flag=True, help="Virtual resolution (metadata only).")
@async_command
async def resolve(node_id, resource, virtual):
    """Resolve a node ID to its value (file chunk)."""
    client = CiteKitClient()
    
    click.echo(f"[RESOLVING] Node: {node_id}")
    try:
        # We need to support the case where node_id is a full address or separate
        if "." in node_id and not resource:
            rid, nid = node_id.split(".", 1)
        else:
            rid, nid = resource, node_id

        if not rid:
            # Try to find which resource contains this node
            click.echo("[!] Resource ID missing. Use --resource or rid.nid format.")
            sys.exit(1)

        evidence = client.resolve(rid, nid, virtual=virtual)
        if virtual:
            click.echo("[SUCCESS] Virtual resolution successful.")
        else:
            click.echo(f"[SUCCESS] Output: {evidence.output_path}")
        click.echo(f"   Modality: {evidence.modality}")
        click.echo(f"   Address: {evidence.address}")
    except Exception as e:
        click.echo(f"[ERROR] {e}", err=True)
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
        click.echo(f"[ERROR] {e}", err=True)
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
            click.echo(f"[INFO] Nodes in '{resource_id}':")
            def print_nodes(nodes, prefix=""):
                for node in nodes:
                    click.echo(f"{prefix}- {node.id} ({node.type}): {node.title}")
                    if node.children:
                        print_nodes(node.children, prefix=prefix + "  ")

            print_nodes(resource_map.nodes)
        except Exception as e:
            click.echo(f"[ERROR] {e}", err=True)
            sys.exit(1)
        return

    # List all resources
    maps = client.list_maps()
    if not maps:
        click.echo("No resources found.")
        return

    click.echo(f"found {len(maps)} resources:")
    for resource_id in maps:
        try:
            resource_map = client.get_map(resource_id)
            click.echo(f" - {resource_map.resource_id} ({resource_map.type}): {resource_map.title}")
        except Exception:
            click.echo(f" - {resource_id} (corrupt)")

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
        click.echo("[!] Resource ID missing. Use --resource or rid.nid format.")
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
            click.echo(f"[ERROR] Node '{nid}' not found in resource '{rid}'.")
            sys.exit(1)
            
        click.echo(f"[INFO] Node: {node.id}")
        click.echo(f"   Resource: {rid} ({resource_map.type})")
        click.echo(f"   Title: {node.title}")
        click.echo(f"   Type: {node.type}")
        click.echo(f"   Location: {node.location}")
        if node.summary:
            click.echo(f"   Summary: {node.summary}")
            
    except Exception as e:
        click.echo(f"[ERROR] {e}", err=True)
        sys.exit(1)

@main.command("check-map")
@click.argument("path", type=click.Path(exists=True))
def check_map(path):
    """Validate a JSON map against the strict schema."""
    from citekit.models import ResourceMap
    from citekit import __version__
    
    click.echo(f"[INFO] Validating {path}...")
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        # Pydantic validation
        map_model = ResourceMap(**data)
        
        click.echo("[SUCCESS] Map is valid.")
        click.echo(f"   Schema Version: {__version__}")
        click.echo(f"   Resource ID: {map_model.resource_id}")
        click.echo(f"   Nodes: {len(map_model.nodes)}")
        
        # Additional logical checks
        if map_model.type == "text":
            text_nodes = [n for n in map_model.nodes if n.location.modality == "text"]
            if not text_nodes:
                click.echo("[WARNING] Map type is 'text' but contains no text-modality nodes.")
                
    except json.JSONDecodeError:
        click.echo("[ERROR] Invalid JSON syntax.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"[ERROR] Validation Failed: {e}", err=True)
        sys.exit(1)

@main.command("adapt")
@click.argument("input_path", type=click.Path(exists=True))
@click.option("--adapter", "-a", required=True, help="Adapter name ('graphrag') or path to custom script.")
@click.option("--output", "-o", help="Output path for the map (default: .resource_maps/<name>.json).")
def adapt(input_path, adapter, output):
    """Convert external data (GraphRAG, etc.) into a CiteKit Map."""
    from citekit.adapters import GraphRAGAdapter, GenericAdapter, LlamaIndexAdapter
    import importlib.util

    click.echo(f"[INFO] Adapting {input_path} using '{adapter}'...")

    try:
        # 1. Resolve Adapter
        adapter_instance = None
        
        if adapter == "graphrag":
            adapter_instance = GraphRAGAdapter()
        elif adapter == "llamaindex":
            adapter_instance = LlamaIndexAdapter()
        elif adapter == "generic":
            adapter_instance = GenericAdapter()
        elif adapter.endswith(".py"):
            # Load custom script
            spec = importlib.util.spec_from_file_location("custom_adapter", adapter)
            if not spec or not spec.loader:
                click.echo(f"[ERROR] Could not load custom adapter from {adapter}", err=True)
                sys.exit(1)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Look for 'adapt' function or 'Adapter' class
            if hasattr(module, "adapt") and callable(module.adapt):
                # Functional adapter wrapper
                class FunctionalAdapter:
                    def adapt(self, data, **kwargs):
                        return module.adapt(data, **kwargs)
                adapter_instance = FunctionalAdapter()
            elif hasattr(module, "Adapter"):
                adapter_instance = module.Adapter()
            else:
                click.echo("[ERROR] Custom script must define an 'adapt(data)' function or 'Adapter' class.", err=True)
                sys.exit(1)
        else:
            click.echo(f"[ERROR] Unknown adapter '{adapter}'. Use 'graphrag', 'llamaindex', 'generic', or a .py file.", err=True)
            sys.exit(1)

        # 2. Run Adaptation
        resource_map = adapter_instance.adapt(input_path)
        
        # 3. Save Output
        if not output:
            output_dir = Path(".resource_maps")
            output_dir.mkdir(exist_ok=True)
            output = output_dir / f"{resource_map.resource_id}.json"
        
        Path(output).write_text(json.dumps(resource_map.model_dump(), indent=2, default=str), encoding="utf-8")
        
        click.echo(f"[SUCCESS] Map adapted and saved to: {output}")
        click.echo(f"   Resource ID: {resource_map.resource_id}")
        click.echo(f"   Nodes: {len(resource_map.nodes)}")

    except Exception as e:
        click.echo(f"[ERROR] Adaptation Failed: {e}", err=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
