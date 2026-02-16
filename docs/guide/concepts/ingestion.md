# Ingestion Process

Ingestion is the phase where CiteKit transforms unstructured media into structured data. It leverages a configured mapper (Gemini by default) to "watch" or "read" the file and output a strict JSON schema. You can also use local models by implementing a custom `MapperProvider`.

## 1. File Hashing & Caching

Before any API calls, CiteKit calculates a **SHA-256 hash** of the input file.

$$ \text{Hash}(File) \rightarrow \text{Cache Key} $$

-   **Hit**: If a `.json` map with this has exists in `.resource_maps/`, it is returned immediately.
-   **Miss**: The file is queued for upload.

This ensures that re-running `ingest()` on the same huge video file is instant and costs zero tokens.

## 2. The Prompt Strategy

CiteKit uses a **hierarchical extraction strategy**. We do not ask for a summary. We ask for a *temporal segmentation*.

The system prompt enforces a specific JSON schema:

```typescript
type Node = {
  id: string;          // Unique slug (e.g., "intro_video")
  title: string;       // Human-readable title
  summary?: string;    // Contextual summary
  start?: number;      // Seconds (Video/Audio)
  end?: number;        // Seconds (Video/Audio)
  pages?: number[];    // Page numbers (PDF)
  children?: Node[];   // Nested structure
}
```

This ensures the LLM output is always machine-readable and valid.

## 3. Supported Context Windows

The default Gemini mapper supports massive context windows, allowing it to process:

-   **Video**: Up to ~1 hour (Flash) or ~10 hours (Pro) depending on token usage.
-   **Audio**: Up to 11 hours.
-   **PDF**: Up to 1000+ pages.
-   **Images**: High-resolution analysis of charts, diagrams, and complex scenes.
-   **Text/Code**: Up to 1M tokens of source code or documentation.

## 4. Visual Analysis Strategy (Images)

For images, CiteKit uses a specialized prompt to detect **Semantic Regions**.

It doesn't just "caption" the image. It returns bounding boxes (`bbox`) for:
-   **Charts & Graphs**: Identifying axes and data regions.
-   **Text Blocks**: locating paragraphs in scanned documents.
-   **Objects**: Identifying key items in a photo.

```json
{
  "id": "chart_sales",
  "title": "Q4 Sales Growth",
  "type": "chart",
  "location": {
    "bbox": [0.1, 0.1, 0.5, 0.5] // [x1, y1, x2, y2]
  }
}
```

## 5. Configuration

You can customize the underlying model in the `CiteKitClient` constructor.

```python
from citekit import CiteKitClient

# default: gemini-1.5-flash (Fast, Cheap)
client = CiteKitClient()

# High-accuracy mode (Slower, More Expensive)
client_pro = CiteKitClient(model="gemini-1.5-pro")
```

| Model (Gemini mapper) | Best For | Speed | Cost |
| :--- | :--- | :--- | :--- |
| **Flash 1.5** | Videos, broad segmentation, standard PDFs | Fast | Low |
| **Pro 1.5** | Dense academic papers, subtle visual details | Slower | Higher |
