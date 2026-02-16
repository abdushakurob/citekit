# Architecture

CiteKit is designed as a **two-phase local-first** system. It separates the expensive, slow process of specific *finding* content from the cheap, fast process of *retrieving* it.

## High-Level Design

The system consists of three main components:

1.  **Ingestion Engine**: Interfaces with a multimodal mapper (Gemini by default) to generate semantic maps.
2.  **Map Storage**: A local JSON-based storage for persisting content structure.
3.  **Resolution Engine**: A local media processing layer (FFmpeg, PyMuPDF) for extracting content.

<div class="mermaid-container" style="width: 100%; display: flex; justify-content: center;">

```mermaid
graph TD
    subgraph "Phase 1: Ingestion (One-time)"
    A[Source File] -->|Binary Stream| B[Mapper API (Gemini default)]
    B -->|Analysis| C[CiteKit Mapper]
    C -->|Structured JSON| D[Resource Map]
    end

    subgraph "Phase 2: Storage (Local)"
    D -->|Write| E[./.resource_maps/]
    end

    subgraph "Phase 3: Context Orchestration (Runtime)"
    App[Agent App] -->|Request Node| F[CiteKit Orchestrator]
    F -->|Read| E
    F -->|Read| A
    F -->|Physical Mode| G[High-Fidelity Evidence]
    F -->|Virtual Mode| H[Deterministic Metadata]
    G -->|Return Path| App
    H -->|Return JSON| App
    end
```

</div>

## 1. The Ingestion Engine

The ingestion process enables "blind" agents to understand file content.

-   **Input**: A file path (PDF, MP4, MP3, JPG, PY, MD, TXT).
-   **Process**:
    1.  The file is uploaded to the configured mapper API (temporarily).
    2.  CiteKit prompts the mapper with a domain-specific schema instruction.
    3.  The model returns a hierarchical JSON structure representing the file's content (Topics, Chapters, Scenes).
    4.  The remote file is deleted from Google's servers (depending on retention policy, usually immediate for temp files).

## 2. Resource Maps (.resource_maps)

The core data structure in CiteKit is the **Resource Map**. It is a normalized JSON format that describes *where* information lives within a file.

Example Structure:
```json
{
  "resource_id": "research_paper_v1",
  "source_path": "abs/path/to/paper.pdf",
  "metadata": { "title": "Attention Is All You Need", "type": "pdf" },
  "nodes": [
    {
      "id": "intro",
      "title": "Introduction",
      "location": { "pages": [1] },
      "context": "Discussion of RNNs and CNNs..."
    },
    {
      "id": "architecture",
      "title": "Model Architecture",
      "location": { "pages": [3, 4, 5] },
      "context": "Detailed diagram of Transformer..."
    }
  ]
}
```

This map allows an agent to "read" the entire structure of a 50-page document in ~500 tokens.

## 3. The Resolution Engine

The resolution engine is completely local and offline. It supports two distinct modes:

### Physical Resolution
Uses specialized libraries to extract byte-perfect segments based on the map's coordinates into new files.

| Modality | Backend Engine | Operation |
| :--- | :--- | :--- |
| **PDF** | `PyMuPDF` / `pdf-lib` | Extracts page ranges into a new single-file PDF. |
| **Video** | `ffmpeg` | Performs stream copy (`-c copy`) for instant cutting without re-encoding. |
| **Audio** | `ffmpeg` | Trims audio streams to specified timestamps. |
| **Image** | `Pillow` / `sharp` | Crops images to specified bounding boxes. |
| **Text** | Native (Python/JS) | Slices file content by line range. |

### Virtual Resolution (Zero-Binary)
Skips the extraction entirely and returns the **conceptual coordinates** (timestamps, page numbers, or bounding boxes) along with a virtual address. This mode has **zero external binary dependencies** (no FFmpeg needed) and is ideal for serverless environments.

## Data Flow

1.  **Developer** calls `client.ingest("video.mp4")`.
2.  **CiteKit** generates `video.json` map.
3.  **Agent** reads `video.json` and decides it needs the "Demo" section.
4.  **Agent** calls `client.resolve("video", "demo", { virtual: true })`.
5.  **CiteKit** identifies timestamps: `180.5` to `210.0`.
6.  **Agent** receives the metadata directly, using it to point an LLM (GenAI File API) at the original file's specific segment.

*The same flow applies to Images (Metadata -> Crop), PDFs (TOC -> Page Extraction), and Code (Structure -> Line Slicing).*
