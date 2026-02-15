# Getting Started

This guide covers the installation and basic usage of the CiteKit SDK.

## Prerequisites

1.  **FFmpeg**: Required for video/audio processing.
    -   **Windows**: [Download build](https://gyan.dev/ffmpeg/builds/) and add to PATH.
    -   **macOS**: `brew install ffmpeg`
    -   **Linux**: `sudo apt install ffmpeg`
    
    *Note: FFmpeg is only required for Video and Audio. PDF and Image support works out of the box.*

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

    // 3. Resolve
    const evidence = await client.resolve(videoMap.resource_id, videoMap.nodes[0].id);
    console.log(`Saved clip to: ${evidence.output_path}`);
}

main();
```

## Next Steps

-   **Architecture**: Understand how CiteKit works under the hood in [Core Concepts](/guide/concepts/architecture).
-   **API Reference**: View the full [Python](/api/python) or [JavaScript](/api/javascript) API docs.
