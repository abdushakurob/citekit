# Virtual Resolution

Virtual Resolution is a CiteKit feature designed for high-performance AI agents and constrained environments. It allows you to "resolve" a content node into its conceptual boundaries (timestamps, pages, or coordinates) without physically extracting files.

## The Problem: The "Binary Hurdle"

Traditional content resolution works like this:
1.  **Map**: Find the "Explanation of Gravity" in a video.
2.  **Physical Resolve**: CiteKit calls **FFmpeg** to cut a 30-second `.mp4` file.
3.  **Consume**: You send that small `.mp4` to your LLM.

**The catch**: Many cloud runtimes (like serverless functions) don't have FFmpeg. Installing it is heavy, slow, and often results in execution timeouts.

## The Solution: Virtual Resolve

Virtual Resolution skips the "Physical" step.
1.  **Map**: Find the "Explanation of Gravity".
2.  **Virtual Resolve**: CiteKit returns the **Timestamps** (`start: 180, end: 210`) immediately.
3.  **Consume**: You send the **Original Video URL** + the **Timestamps** to a modern Multimodal LLM (like Gemini 1.5).

### Why this is better:
-   **Zero Binary Dependencies**: No FFmpeg/Sharp/Pdf-lib required at runtime.
-   **Sub-millisecond Speed**: No file I/O or heavy processing.
-   **Native AI Support**: Most vision models prefer "original file + metadata" over cropped fragments for better context.

---

## How to use it

### JavaScript
```javascript
const evidence = await client.resolve('resource-id', 'node-id', { virtual: true });

// evidence.output_path is undefined
// use evidence.node.location for the metadata
const { start, end } = evidence.node.location;
```

### Python
```python
evidence = client.resolve('resource-id', 'node-id', virtual=True)

# No file created on disk
start_time = evidence.node.location.start
end_time = evidence.node.location.end
```

### Model Context Protocol (MCP)
If you are using the CiteKit MCP server, you can pass the `virtual` parameter to the `resolve` tool:
```json
{
  "name": "citekit/resolve",
  "arguments": {
    "resource_id": "lecture",
    "node_id": "intro",
    "virtual": true
  }
}
```

---

## Output Structure

When `virtual: true` is passed, the `ResolvedEvidence` object looks like this:

| Field | Type | Description |
| :--- | :--- | :--- |
| `modality` | `string` | The media type (`video`, `document`, etc.) |
| `address` | `string` | A URI pointer, e.g., `video://lecture#t=180,210` |
| `node` | `Node` | The full node object with its `location` metadata. |
| `output_path` | `null` | **Empty**. No file was generated. |

## Use Cases

### 1. Serverless Video Pipeline
Use Virtual Resolve in cloud functions to extract metadata, then use a signed URL to point your LLM at specific timestamps in S3/Cloudinary.

### 2. High-Density Agents
If an agent needs to cite 50 different parts of a book, generating 50 mini-PDFs is slow. Use Virtual Resolve to get the page numbers instantly and ground the agent's response.

### 3. Frontend Clipping
In a React app, use the virtual resolved timestamps to set the `currentTime` of a `<video>` tag.

---

## Best Practices: The "Virtual Pointer" Protocol

When storing resolved evidence in your database, we recommend prefixing virtual addresses to distinguish them from physical file URLs.

> [!TIP]
> **Observation**: Using a `virtual:` prefix helps your frontend logic instantly decide whether to fetch a file or just seek to a timestamp.
>
> 1. **Physical**: `https://cdn.example.com/resolved/clip_1.mp4`
> 2. **Virtual**: `virtual:video://original#t=180,210`
