# Overview

**CiteKit** is an open-source, local-first SDK that enables AI agents to reference specific parts of multimodal files (PDFs, Videos, Audio, Images, Code) without hallucinating.

It solves the *context granularity* problem:
> "How do I give my agent access to a 2-hour video or 500-page PDF without blowing up the context window?"

CiteKit answers this by **mapping the file structure first**, letting the agent **choose** relevant sections, and then **extracting** only those sections locally.

## Key Features

-   **Zero-Cloud Extraction**: Uses local `ffmpeg` and PDF engines to extract content. No proprietary cloud needed for the extraction phase.
-   **Universal Map Protocol**: A standardized JSON schema for representing content structure across any modality.
-   **Multimodal**:
    -   **PDF**: Extract specific page ranges (as a clean, smaller PDF).
    -   **Video**: Extract clips by time range (frame-perfect standard copy).
    -   **Audio**: Extract segments by time range.
    -   **Images**: Extract regions by bounding box.
    -   **Text/Code**: Slices content by line range.
-   **Agent-Ready**: Designed for MCP (Model Context Protocol), LangChain, and other agentic frameworks.

## Supported Modalities

| Type | Input Formats | What Gets Extracted |
| :--- | :--- | :--- |
| **Document** | `.pdf` | Specific pages (clean PDF subset). |
| **Video** | `.mp4`, `.mov`, `.mkv` | Exact clips (time range) via stream copy. |
| **Audio** | `.mp3`, `.wav`, `.m4a` | Exact segments (time range). |
| **Image** | `.jpg`, `.png`, `.webp` | Semantic regions (charts, objects) as cropped images. |
| **Text** | `.txt`, `.md`, `.py`, `.js` | Structural blocks & line-range slices. |

## Why Use CiteKit?

In the current era of **Agentic AI** and **Long-Context Models**, discovery is only half the battle. CiteKit provides the high-fidelity **Context Orchestration** required for production-grade reliability.

| Modern Problem | CiteKit Solution |
| :--- | :--- |
| **Agentic Loops** | Provides deterministic tools (`resolve`) that let agents navigate files like expert researchers. |
| **Attention Loss** | Minimizes "Lost in the Middle" by sending only relevant, structurally coherent segments to LLMs. |
| **Multimodal Blindspots** | Bridges the gap between text-based RAG and visual/temporal evidence (Video/PDF). |
| **Context Overload** | Enables **Context Caching** and **Semantic Partitioning** to keep latency and costs low. |

## How It Works: The Two-Phase Lifecycle

CiteKit operates on a "Map-Resolve" pattern to maximize context efficiency:

1.  **Phase 1: Ingestion (Cloud-Mapped)**
    You pass a file to CiteKit. It is uploaded to the configured mapper (Gemini by default) where a multimodal model analyzes its structural "DNA" to generate a JSON Resource Map. This consumes context tokens **once**.
    If you want to avoid cloud ingestion, you can use a local model by implementing a custom `MapperProvider` (see [Custom Mappers](/guide/custom-mappers)).
    
2.  **Phase 2: Resolution (Local-First)**
    Once the map (JSON) is stored locally, the cloud is no longer needed. Agents can query the map and resolve high-fidelity clips or pages 100% locally from your disk.

> [!IMPORTANT]
> **Context Economics**: For a 2-hour video, you might use 100k tokens *once* for mapping. From then on, an agent can "see" the entire structure in ~1k tokens of JSON, and "resolve" any segment without ever sending the video to the cloud again.

## Deployment Choice

CiteKit is designed for the modern edge:
- **Local Native**: Full FFmpeg/PDF extraction for desktop apps and high-performance servers.
- **[Virtual Resolution](/guide/concepts/virtual-mode)**: Metadata-only resolution for **Zero-Binary Serverless** environments (Vercel/Lambda).

## Architecture & Integration

- [**The Modern Stack**](/guide/modern-stack) - See how CiteKit fits with Agentic RAG, GraphRAG, and Long-Context models.
- [**Contextual Retrieval**](/guide/concepts/content-resolution) - Learn about frame-perfect and page-perfect orchestration.
- [**Agentic Examples**](/guide/examples/research-app) - Practical implementations for Research, Study, and Search agents.

[Get Started with CiteKit →](/guide/getting-started)
