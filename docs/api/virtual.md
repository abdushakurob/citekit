# Virtual Resolution API

Technical specification for Virtual Resolution in CiteKit.

## Overview

When passing `virtual: true` to the `resolve` method, CiteKit bypasses the physical extraction process (FFmpeg/Sharp) and returns metadata instantly.

## Resolution Parameters

### JavaScript
```typescript
await client.resolve(resourceId: string, nodeId: string, options: { virtual: boolean });
```

### Python
```python
client.resolve(resource_id: str, node_id: str, virtual: bool = True)
```

## `ResolvedEvidence` (Virtual Mode)

When `virtual` is `true`, the `ResolvedEvidence` object has the following state:

| Property | Type | Value / Description |
| :--- | :--- | :--- |
| `modality` | `string` | `video`, `audio`, `document`, or `image`. |
| `address` | `string` | The CiteKit URI pointer (e.g., `video://lecture#t=180,210`). |
| `node` | `Node` | The full node object including `location` metadata. |
| `output_path` | `null` | **Empty**. No file was generated. |

---

## Use Cases

### 1. Serverless Video Pipeline
Use Virtual Resolve in cloud functions to extract metadata, then use a signed URL to point your LLM at specific timestamps in S3/Cloudinary.

### 2. High-Density Agents
If an agent needs to cite 50 different parts of a book, generating 50 mini-PDFs is slow. Use Virtual Resolve to get the page numbers instantly and ground the agent's response.

### 3. Frontend Clipping
In a React app, use the virtual resolved timestamps to set the `currentTime` of a `<video>` tag.

---

## URI Addressing Format
...

CiteKit uses a custom URI scheme to represent virtual slices accurately.

### Structure
`scheme://<resource_id>#<fragment>`

### Schemes & Modalities

| Scheme | Modality | Fragment Key | Example |
| :--- | :--- | :--- | :--- |
| `doc` | `document` | `pages` | `doc://book#pages=12-15` |
| `video` | `video` | `t` | `video://lecture#t=60-90` |
| `audio` | `audio` | `t` | `audio://meeting#t=10.5-20.0` |
| `image` | `image` | `bbox` | `image://diagram#bbox=0.1,0.1,0.5,0.5` |

### Fragment Grammar

- **Time Range (`t`)**: `start-end` (in seconds or HH:MM:SS format).
- **Page Range (`pages`)**: `start-end` (consecutive) or `p1,p2,p3` (comma-separated).
- **Bounding Box (`bbox`)**: `x1,y1,x2,y2` (normalized 0.0 to 1.0).

---

## Best Practices

### The `virtual:` Prefix
When storing these addresses in a database, it is recommended to prefix them with `virtual:` to help your frontend logic decide whether to fetch a physical file or just seek to a timestamp.

**Example**: `virtual:video://lecture#t=60-90`
