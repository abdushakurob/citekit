# Example: Temporal Content Orchestration (Python)

In this guide, we'll build a **Video Orchestration** tool. It lets you "search" inside a library of videos not just by keywords, but by **Concepts**, and plays the exact temporal segment where those concepts are mastered.

This demonstrates using the **Python SDK** for **Temporal Content Orchestration** in modern agentic loops.

## The Strategy: Concept-Based Navigation

Standard video search relies on "rough" transcription chunks. CiteKit enables a more sophisticated agentic workflow:
1.  **Structural Mapping**: Ingest the video via the configured mapper (Gemini by default) to discover its semantic chapters and scenes (cloud-side once).
2.  **Deterministic Retrieval**: After mapping, all navigation and extraction is 100% local.
3.  **Zero-Latency Switching**: Use **Virtual Resolution** for cloud agents or **Physical Extraction** for local desktop experiences.

## Implementation (`orchestrate_video.py`)

```python
import click
import os
import subprocess
import asyncio
from citekit import CiteKitClient

# CiteKit acts as our temporal orchestrator
client = CiteKitClient()

@click.group()
def cli():
    """Video Orchestrator: Semantic Timeline Navigation"""
    pass

@cli.command()
@click.argument('directory', type=click.Path(exists=True))
def index(directory):
    """Orchestrate: Generate structural maps for a video library."""
    files = [f for f in os.listdir(directory) if f.endswith(('.mp4', '.mov', '.mkv'))]
    
    async def _process():
        for f in files:
            path = os.path.join(directory, f)
            print(f"[INFO] Mapping Structural DNA: {f}")
            await client.ingest(path, "video")

    asyncio.run(_process())

@cli.command()
@click.argument('concept')
def seek(concept):
    """Seek: Find a concept and play the high-fidelity clip."""
    
    async def _search():
        # CiteKit provides the list of all semantic maps
        resource_ids = client.list_maps()
        
        for rid in resource_ids:
            resource_map = client.get_map(rid)
            # Find the node that matches the concept
            # (In a real Agent, an LLM would choose the node based on summaries)
            for node in resource_map.nodes:
                if concept.lower() in node.id.lower() or concept.lower() in (node.summary or "").lower():
                    print(f"[INFO] Concept Found in {rid}: {node.title}")
                    
                    # Resolve to a physical high-fidelity clip
                    evidence = client.resolve(rid, node.id)
                    
                    # Orchestrate the playback
                    print(f"[PLAYING] {evidence.output_path}")
                    subprocess.run(["mpv", evidence.output_path])
                    return

    asyncio.run(_search())

if __name__ == '__main__':
    cli()
```

## Why this is "Modern"

### 1. From Keywords to Concepts
While basic retrieval might return a fixed-window around a keyword, **Temporal Orchestration** returns the **logical unit**. If a professor explains a proof over 5 minutes, CiteKit gives you all 5 minutes. No more cut-off explanations.

### 2. Multi-Step Retrieval
In an Agentic Loop (like ReAct), the agent can:
1.  `list_maps()` to see the library.
2.  `get_map()` to "read" the video timeline in seconds.
3.  `resolve()` to extract only the evidence it needs to reason.

### 3. Agentic Grounding
Because the retrieval is **deterministic** (based on the map), the agent can ground its response with stable CiteKit URIs (`video://lex#t=180-210`), making it compatible with **Context Caching** for ultra-low latency future runs.
