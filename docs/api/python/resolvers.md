# Python Resolvers & Adapters

## Resolvers

Resolvers handle the physical extraction of content (clips, page slices, etc.). CiteKit includes built-in resolvers for:

-   **Video**: Uses `ffmpeg`.
-   **Audio**: Uses `ffmpeg`.
-   **Document**: Uses `PyMuPDF`.
-   **Image**: Uses `PIL`.
-   **Text**: Native line extract.

---

## Adapters

Adapters convert external data formats into CiteKit `ResourceMap` objects.

### `GraphRAGAdapter`
Maps GraphRAG entities/communities to CiteKit nodes.

### `LlamaIndexAdapter`
Maps LlamaIndex nodes to CiteKit nodes.

### Custom Adapters
Implement a class or script with an `adapt()` method.
