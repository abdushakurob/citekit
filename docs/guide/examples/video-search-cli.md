# Build a Video Search CLI (Python)

In this example, we'll build a command-line tool that lets you "search" inside a folder of videos. You ask a question, and it plays the exact clip where the answer is discussed.

This demonstrates using the **Python SDK** to build a RAG-alternative for video libraries.

## Prerequisites

-   Python 3.10+
-   `setup.py` or just install dependencies: `pip install citekit click mpv-player`
-   (Optional) `mpv` installed on your system to play the video.

## 1. The Strategy

Instead of transcribing the video and searching text (Standard RAG), we will:
1.  **Map** the video structure using CiteKit.
2.  **Filter** the structure for relevant topics.
3.  **Resolve** the relevant node to a clip.
4.  **Play** the clip using a media player.

## 2. The Code (`videase.py`)

```python
import click
import os
import subprocess
import asyncio
from typing import List
from citekit import CiteKitClient

# Initialize Client
client = CiteKitClient()

@click.group()
def cli():
    """Videase: Video Search Engine"""
    pass

@cli.command()
@click.argument('directory', type=click.Path(exists=True))
def ingest(directory):
    """Scan a directory and index all videos."""
    files = [f for f in os.listdir(directory) if f.endswith(('.mp4', '.mov', '.mkv'))]
    click.echo(f"Found {len(files)} videos.")

    async def _process():
        for f in files:
            path = os.path.join(directory, f)
            click.echo(f"Indexing {f}...")
            # This generates the map (cached if repeated)
            await client.ingest(path, "video")
            click.echo("Done.")

    asyncio.run(_process())

@cli.command()
@click.argument('query')
def search(query):
    """Search for a concept and play the clip."""
    
    async def _search():
        # 1. List all known maps
        resource_ids = client.list_maps()
        matches = []

        click.echo(f"Searching {len(resource_ids)} videos for '{query}'...")

        # 2. Naive Search (In production, use an LLM here to pick nodes)
        # We search the 'summary' and 'id' of nodes in the JSON map.
        for rid in resource_ids:
            structure = client.get_structure(rid)
            for node in structure.nodes:
                text = (f"{node.id} {node.summary}").lower()
                if query.lower() in text:
                    matches.append((rid, node))

        if not matches:
            click.echo("No matches found.")
            return

        # 3. Present options
        for i, (rid, node) in enumerate(matches):
            click.echo(f"[{i}] {rid}: {node.id} ({node.start}s - {node.end}s)")

        # 4. User selection
        choice = click.prompt("Play which clip?", type=int)
        selected_rid, selected_node = matches[choice]

        # 5. Resolve (Stream Copy)
        click.echo("Extracting clip...")
        evidence = await client.resolve(selected_rid, selected_node.id)
        
        # 6. Play
        click.echo(f"Playing {evidence.output_path}...")
        subprocess.run(["mpv", evidence.output_path])

    asyncio.run(_search())

if __name__ == '__main__':
    cli()
```

## 3. Usage

```bash
# Index your lecture folder
python videase.py ingest ./lectures

# Find where "Gradient Descent" is discussed
python videase.py search "gradient"
```

## Why this approach vs. VectorDB?

### Standard Video RAG
-   **Method**: Transcribe video -> Chunk text -> Embed -> Vector Search.
-   **Result**: You search "Gradient Descent". The DB returns a 30-second chunk *around* the word.
-   **Problem**: The professor might strictly define it for 5 minutes. The 30s chunk cuts off the explanation. Or the word is mentioned in passing in a different context.

### CiteKit Approach (Structural)
-   **Method**: LLM maps visual/audio structure -> Search Map -> Extract Node.
-   **Result**: You search "Gradient Descent". The Map contains a node `id: "gradient_descent_explanation"` with `start: 600, end: 900`.
-   **Outcome**: You get the **entire 5-minute explanation**. The retrieval unit is the **concept**, not the keyword.
