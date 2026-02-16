# Getting Started

This guide covers the installation and core lifecycle of the CiteKit SDK.

## Prerequisites

1.  **FFmpeg** (Required for Video/Audio):
    CiteKit uses local FFmpeg to extract high-fidelity clips. Ensure it is installed and available in your system `PATH`.
    -   **Windows**: [Download build](https://gyan.dev/ffmpeg/builds/) and add the `bin` folder to your Path.
    -   **macOS**: `brew install ffmpeg`
    -   **Linux**: `sudo apt install ffmpeg`
    
    > [!TIP]
    > To verify, run `ffmpeg -version` in your terminal. If you see version info, you are ready.

2.  **Mapper API Key** (Gemini by default): 
    Required only for the **Ingestion** (Mapping) phase. Resolution is 100% local. If you prefer local models, use a custom mapper instead (see [Custom Mappers](/guide/custom-mappers)).
    -   Get a key from [Google AI Studio](https://aistudio.google.com/app/apikey) if you use the default Gemini mapper.
    -   Set it as an environment variable: `GEMINI_API_KEY` (default mapper only).

## Installation

### Python
```bash
pip install citekit
```

### Node.js
```bash
npm install citekit
```

---

## The 3-Step Lifecycle

CiteKit follows a simple **Ingest → Map → Resolve** flow.

### 1. Ingest (CLI)
The fastest way to get started is using the CLI to map your documents. The API key must be in your environment (default Gemini mapper) unless you supply a custom mapper in code.

```bash
# General Syntax: citekit ingest <file> --type <modality>
citekit ingest lecture.mp4 --type video
```
*This generates a JSON map in the `.resource_maps/` directory.*

### 2. Connect (SDK)
Load the map into your application logic.

#### Python
```python
from citekit import CiteKitClient

client = CiteKitClient() # Automatically reads GEMINI_API_KEY from env (Gemini default)
resource_map = client.get_map("lecture")
print(f"Nodes found: {len(resource_map.nodes)}")
```

#### Node.js
```typescript
import { CiteKitClient } from 'citekit';

const client = new CiteKitClient();
const resourceMap = client.getMap('lecture');
```

### 3. Resolve (Extract)
Extract a specific node (a scene, a page, or a function) to disk.

```python
# Returns an object with 'output_path' to the clipped file
evidence = client.resolve("lecture", "intro_scene")
print(f"Evidence saved to: {evidence.output_path}")
```

---

## Next Steps

-   **Deep Dive**: Learn how CiteKit handles [Coordinate Systems](/api/models) with industrial precision.
-   **CLI Reference**: View every command in the [CLI docs](/api/cli/).
-   **MCP Integration**: Connect CiteKit directly to Claude or Cursor in the [MCP guide](/api/mcp/).

> [!IMPORTANT]
> **Environment Context**: By default, CiteKit creates `.resource_maps/` and `.citekit_output/` in your current working directory. You can change these by passing `storage_dir` and `output_dir` to the constructor.
