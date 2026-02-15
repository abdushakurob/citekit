# Content Resolution

**Resolution** is the process of extracting a specific segment from a source file based on a `ResourceNode`.

## Modes of Resolution

CiteKit supports two modes of resolution depending on your environment:

1.  **Physical Resolution** (Default): Extracts a new file (clip, mini-PDF, crop) to your disk. Requires local binaries like FFmpeg.
2.  **Virtual Resolution**: Returns only the metadata (timestamps, pages, bounding boxes) without creating a file. **Perfect for serverless and direct AI model consumption.**

See the [Virtual Resolution Guide](/guide/concepts/virtual-mode) for more.

## Mechanism by Modality (Physical)

### 1. Video & Audio (FFmpeg)

CiteKit uses `ffmpeg` for frame-accurate, lossless extraction.

**Key Command**:
```bash
ffmpeg -ss <start> -to <end> -i <input> -c copy <output>
```

-   `-ss` / `-to`: Seek to precise timestamps.
-   `-c copy`: **Stream Copy**. This instructs FFmpeg to copy the audio/video bitstreams directly without re-encoding.
    -   **Speed**: Near instant (>100x variance).
    -   **Quality**: 100% lossless (bit-perfect clone).

### 2. PDF (PyMuPDF / pdf-lib)

CiteKit creates a valid, standalone PDF for the requested page range.

-   **Process**:
    1.  Open source PDF.
    2.  Create new empty PDF.
    3.  Copy pages `[start_page...end_page]` to new PDF.
    4.  Save.
-   **Output**: A clean PDF file containing only relevant context, preserving all vectors, text layers, and images.

### 3. Images (Pillow / Sharp)

CiteKit creates a new image file cropped to the semantic region of interest.

-   **Process**:
    1.  Load image.
    2.  Crop to `bbox: [x, y, w, h]`.
    3.  Save as original format (JPG/PNG).

## Caching Strategy

Resolved evidences are hashed and cached in `.citekit_output/`.

$$ \text{Cache Key} = \text{Hash}(\text{Source Path} + \text{Node ID}) $$

If an agent requests the same segment twice, the file system path is returned instantly without re-processing.

### Best Practice: Reuse Resolved Nodes

Agents should be aware that `resolve()` operations, while fast for audio/video stream-copy, still involve file I/O.

**Recommendation**:
Before calling `resolve()`, check if you already have the evidence. CiteKit handles this internally, but your agent logic can also track "active" evidence.

1.  **Internal Caching**: CiteKit checks `.citekit_output` first. If the file exists and matches the hash, it returns the path immediately.
2.  **Agent Persistence**: If your agent runs across multiple sessions, consider persisting the mapping of `node_id` -> `local_path` to avoid even the micro-latency of the hash check.
