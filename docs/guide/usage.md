# Usage Guide

This guide covers the core operations of CiteKit: **Ingesting** (Mapping), **Inspecting** (Planning), and **Resolving** (Extracting).

::: tip
CiteKit is designed to be **isomorphic**. You can mix and match interfaces (e.g., Ingest via CLI, Resolve via Python).
:::

- [Ingestion](./usage.md#1-ingesting-resources)
- [Inspection](./usage.md#2-inspecting-maps)
- [Resolution](./usage.md#3-resolving-content)
- [Map Adapters](./adapters.md)

## 1. Ingesting Resources

Ingestion is the process of analyzing a file (Video, Audio, PDF, Text) to create a **Resource Map**. This is the only step that requires a mapper (Gemini by default, or a custom `MapperProvider` for local models).

::: code-group

```bash [CLI]
# Ingest a video
python -m citekit.cli ingest lecture.mp4 --type video

# Ingest a text file (code/docs)
python -m citekit.cli ingest README.md --type text
```

```python [Python]
from citekit import CiteKitClient
import asyncio

async def main():
    client = CiteKitClient()
    
    # Ingest video
    video_map = await client.ingest("lecture.mp4", "video")
    print(f"Mapped: {video_map.resource_id}")

    # Ingest text
    text_map = await client.ingest("README.md", "document")

if __name__ == "__main__":
    asyncio.run(main())
```

```typescript [Node.js]
import { CiteKitClient } from 'citekit';

async function main() {
    const client = new CiteKitClient();

    // Ingest video
    const videoMap = await client.ingest('./lecture.mp4', 'video');
    console.log(`Mapped: ${videoMap.resource_id}`);

    // Ingest text
    const textMap = await client.ingest('./README.md', 'document');
}

main();
```

:::

## 2. Inspecting Maps

Once ingested, you can inspect the **Resource Map** to see the structured nodes (chapters, sections, classes) available for resolution.

::: code-group

```bash [CLI]
# List all ingested resources
python -m citekit.cli list

# Inspect nodes within a specific resource
python -m citekit.cli list lecture

# Inspect specific node details
python -m citekit.cli inspect lecture.intro_scene
```

```python [Python]
# Get the full map object
video_map = client.get_map("lecture")

# Iterate nodes
for node in video_map.nodes:
    print(f"ID: {node.id}, Type: {node.type}")
```

```typescript [Node.js]
// Get the full map object
const videoMap = client.getStructure("lecture");

// Iterate nodes
videoMap.nodes.forEach(node => {
    console.log(`ID: ${node.id}, Type: ${node.type}`);
});
```

:::

## 3. Resolving Content

Resolution is the process of extracting the high-fidelity selection (clip, crop, slice) based on a Node ID. This happens **locally**.

::: code-group

```bash [CLI]
# Resolve a node to a file
python -m citekit.cli resolve lecture intro_scene

# Output: .citekit_output/lecture_intro_scene_t_0-30.mp4
```

```python [Python]
# Resolve to physical file
evidence = client.resolve("lecture", "intro_scene")
print(f"Path: {evidence.output_path}")

# Resolve to metadata only (Virtual)
meta = client.resolve("lecture", "intro_scene", virtual=True)
print(f"Time range: {meta.node.location.start} - {meta.node.location.end}")
```

```typescript [Node.js]
// Resolve to physical file
const evidence = await client.resolve("lecture", "intro_scene");
console.log(`Path: ${evidence.output_path}`);

// Resolve to metadata only (Virtual)
const meta = await client.resolve("lecture", "intro_scene", { virtual: true });
console.log(`Time range: ${meta.node.location.start} - ${meta.node.location.end}`);
```

:::

## 4. Using with AI Agents

If you are building an agent, you rarely call these manually. Instead, you use the MCP tools.

| Tool | Purpose |
| :--- | :--- |
| `listResources` | Agent asks "What files do I have?" |
| `getStructure(resource_id)` | Agent asks "What is inside 'lecture'?" |
| `getNode(resource_id, node_id)` | Agent peeks at details of a specific node. |
| `resolve(resource_id, node_id)` | Agent says "Give me that clip/page." |

See [MCP Integration](/integration/mcp) for setup details.
