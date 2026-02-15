# Overview

**CiteKit** is an open-source, local-first SDK that enables AI agents to reference specific parts of multimodal files (PDFs, Videos, Audio, Images) without hallucinating.

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
-   **Agent-Ready**: Designed for MCP (Model Context Protocol), LangChain, and other agentic frameworks.

## Supported Modalities

| Type | Input Formats | What Gets Extracted |
| :--- | :--- | :--- |
| **Document** | `.pdf` | Specific pages (clean PDF subset). |
| **Video** | `.mp4`, `.mov`, `.mkv` | Exact clips (time range) via stream copy. |
| **Audio** | `.mp3`, `.wav`, `.m4a` | Exact segments (time range). |
| **Image** | `.jpg`, `.png`, `.webp` | Semantic regions (charts, objects) as cropped images. |

## Why Use CiteKit?

| Feature | Without CiteKit | With CiteKit |
| :--- | :--- | :--- |
| **Context Strategy** | "Stuff the whole file" (expensive/impossible) or "Arbitrary chunking" (loss of context). | **Semantic Selection**: Agent sees a map of chapters/scenes and picks exactly what it needs. |
| **Privacy** | Uploading full files to 3rd party APIs for every query. | **Local Processing**: Verification/extraction happens on `localhost`. Only the initial mapping uses an LLM. |
| **Accuracy** | Vector search (RAG) often returns irrelevant chunks. | **Deterministic**: If an agent asks for "Introduction", they get exactly the introduction node. |

## How It Works

1.  **Ingest**: You pass a file to CiteKit. It uses a Multimodal LLM (Gemini 1.5) *once* to generate a structural map.
2.  **Store**: The map is saved locally (JSON).
3.  **Resolve**: When an agent wants "Section 3.1", CiteKit instantly extracts those pages/seconds from the original file on your disk.

## Installation

```bash
# Python
pip install citekit
# Installs SDK & CLI

# Node.js
npm install citekit
# To use the CLI (serve command)
npm install -g citekit
```

[Get Started Now →](/guide/getting-started)
