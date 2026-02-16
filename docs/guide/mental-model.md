# Design Philosophy: Stability vs. Flexibility

CiteKit is built on a single core philosophy: **Separating structure from source.**

## What Stays the Same? (The Protocol)

The core **ResourceMap Schema** is the stable contract of CiteKit. Defined in `citekit.models`, it acts like the "HTML" of multimodal content.

| Component | Status | Description |
| :--- | :--- | :--- |
| **ResourceMap** | 🔒 **Stable** | The JSON structure (`nodes`, `id`, `metadata`) is versioned and backward-compatible. |
| **Location** | 🔒 **Stable** | The coordinate system (`seconds`, `pages`, `lines`) is fixed for each modality. |
| **Node** | 🔒 **Stable** | The recursive unit of meaning. A node is always a node, whether it's a video chapter or a code function. |

**Impact:** Agents written today against the `v0.1` schema will work tomorrow, even if the underlying AI models or data sources change.

## What Changes? (The Adapters)

The **Adapters** and **Mappers** are the flexible layer. They are the "Parsers" that turn the messy outside world into clean ResourceMaps.

| Component | Status | Description |
| :--- | :--- | :--- |
| **Mappers** | ⚡ **Flexible** | How we analyze files (Gemini 1.5, GPT-4o, Local Llama3). You can swap these out anytime without breaking the agent. |
| **Adapters** | ⚡ **Flexible** | How we ingest external data (GraphRAG, LlamaIndex, CSVs). You can add new adapters for proprietary formats. |
| **Resolvers** | ⚡ **Flexible** | How we extract bits (FFmpeg, PyMuPDF). You can swap basic `TextResolver` for a fancy `SemanticTextResolver`. |

## Version Stability

While semantic software evolves rapidly, CiteKit's versioning strategy focuses on Schema Stability:

*   **v0.1** establishes the **Schema** (The recursive Node/Location structure).
*   **v0.2+** focuses on expanding the ecosystem of **Adapters** and **Resolvers**.

**The Schema is the foundation.** We have already stabilized the schema for:
*   ✅ Video (Temporal ranges)
*   ✅ Audio (Temporal ranges)
*   ✅ Documents (Page ranges)
*   ✅ Images (Bounding boxes)
*   ✅ Text/Code (Line ranges)

## System Overview (Current State)

We have built a **Universal Multimodal Indexing Engine**.

1.  **Input**: Anything (PDF, MP4, Source Code, GraphRAG JSON).
2.  **Process**: Mapped/Adapted into standard **ResourceMaps**.
3.  **Storage**: Saved locally (`.resource_maps/`).
4.  **Runtime**: Agents request "Node IDs" -> CiteKit gives them "Evidence" (Files or Metadata).

This separation means you can upgrade your *Ingestion* (e.g., switch from Gemini to GPT-5) without changing a single line of your *Agent* code.
