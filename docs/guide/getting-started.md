# Getting Started

This guide covers the installation and basic usage of the CiteKit SDK.

## Prerequisites

1.  **FFmpeg** (Optional): Required for *physical* video/audio processing.
    -   **Windows**: [Download build](https://gyan.dev/ffmpeg/builds/) and add to PATH.
    -   **macOS**: `brew install ffmpeg`
    -   **Linux**: `sudo apt install ffmpeg`
    
    > [!NOTE]
    > If you only need **Virtual Resolution** (metadata/timestamps) or are running in an environment where you cannot install binaries, FFmpeg is **NOT** required. See [Virtual Resolution](/guide/concepts/virtual-mode).

2.  **Gemini API Key**: Required for the ingestion phase.
    -   Get a key from [Google AI Studio](https://makersuite.google.com/app/apikey).
    -   Set environment variable: `GEMINI_API_KEY`.

## Installation

### Python
```bash
pip install citekit
# Installs the SDK and the `python -m citekit.cli` tool.
```

### Node.js
```bash
npm install citekit
```

## Hello World

This example demonstrates the full lifecycle: Ingest -> Map -> Resolve.

### Python

```python
import asyncio
import os
from citekit import CiteKitClient

async def main():
    client = CiteKitClient(api_key=os.environ.get("GEMINI_API_KEY"))

    # Example 1: Video
    print("Ingesting video...")
    video_map = await client.ingest("local_video.mp4", "video")
    
    # Example 2: Image
    print("Ingesting chart...")
    chart_map = await client.ingest("quarterly_report.png", "image")
    print(f"Found {len(chart_map.nodes)} regions in image.")
    
    # Example 3: Code/Text
    print("Ingesting code...")
    code_map = await client.ingest("main.py", "text")
    print(f"Mapped {len(code_map.nodes)} functions/classes.")

    # 3. Resolve (Extract Content)
    # Extracts the specific region (x,y,w,h) as a new image file
    evidence = await client.resolve(chart_map.resource_id, chart_map.nodes[0].id)
    print(f"Saved crop to: {evidence.output_path}")

if __name__ == "__main__":
    asyncio.run(main())
```

### TypeScript / JavaScript

```typescript
import { CiteKitClient } from 'citekit';

async function main() {
    // 1. Initialize Client
    const client = new CiteKitClient();

    // Example 1: Ingest Video
    console.log("Ingesting video...");
    const videoMap = await client.ingest('./local_video.mp4', 'video');
    console.log(`Generated map with ${videoMap.nodes.length} nodes.`);

    // Example 2: Ingest Image
    console.log("Ingesting chart...");
    const chartMap = await client.ingest('./chart.png', 'image');
    console.log(`Found ${chartMap.nodes.length} regions.`);

    // Example 3: Ingest Code
    console.log("Ingesting code...");
    const codeMap = await client.ingest('./main.ts', 'text');
    console.log(`Mapped structure of code.`);

    // 3. Resolve
    const evidence = await client.resolve(videoMap.resource_id, videoMap.nodes[0].id);
    console.log(`Saved clip to: ${evidence.output_path}`);
}

main();

### Command Line Interface (CLI)

The CLI is perfect for testing or simple scripting without writing code.

```bash
# 1. Ingest (Map)
python -m citekit.cli ingest lecture.mp4 --type video

# 2. Resolve (Extract)
# Extracts the node with ID "intro_scene"
python -m citekit.cli resolve lecture intro_scene
```

## Next Steps

-   **Architecture**: Understand how CiteKit works under the hood in [Core Concepts](/guide/concepts/architecture).
-   **API Reference**: View the full [Python](/api/python) or [JavaScript](/api/javascript) API docs.
-   **Deployment**: Learn how to configure CiteKit for [Vercel and AWS Lambda](/guide/deployment).

> [!TIP]
> **Running on Vercel or AWS Lambda?**
> Set the `baseDir` to `/tmp` in your `CiteKitClient` configuration to support the read-only filesystem!
