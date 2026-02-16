# Deployment Guide

Deploying an application that uses CiteKit requires careful consideration of the **Runtime Environment**, specifically regarding FFmpeg availability.

## Serverless & Constrained Runtimes

CiteKit is designed to work seamlessly in restricted environments like AWS Lambda, Vercel, or other serverless functions.

### Read-only Filesystems
Most serverless runtimes have a read-only filesystem except for the `/tmp` directory. To avoid errors, use the `baseDir` option:

```javascript
const client = new CiteKitClient({
  baseDir: require('os').tmpdir()
});
```

> [!WARNING]
> **Vercel Execution Limits**: Ingestion (mapping) can take 15–30 seconds for large files. Standard Vercel Hobby plans have a 10s timeout. Consider using Background Jobs or upgrading to Pro if you ingest large files dynamically.

### Bundle Size & Optional Dependencies
CiteKit follows a "pay-for-what-you-use" model for dependencies. Large libraries like `sharp`, `fluent-ffmpeg`, and `pdf-lib` are lazy-loaded. 
- You do **not** need to install them if you only use CiteKit for mapping/ingestion.
- They are only required if you explicitly call `resolve()` on specific modalities.

### Zero Browser Dependencies
We have removed all browser-centric libraries (like `pdf-parse`) to eliminate `DOMMatrix` or `Canvas` related errors that typically plague PDF processing in Node.js environments.

### The "Virtual Mode" Solution (Binary-Free)

If you are running in an environment where you cannot or do not want to install FFmpeg, you can still use CiteKit for video, audio, and text by using **Virtual Resolution**.

Instead of creating a physical clip, CiteKit returns the exact timestamp metadata. You can then pass these timestamps to your LLM API (like Gemini's `startOffset`) or use them in your frontend video player.

```javascript
// Serverless-safe resolution
const evidence = await client.resolve(vid, node, { virtual: true });

console.log(evidence.node.location.start); // e.g., 180.5
```

## Docker (Recommended)

Docker is the most reliable way to deploy CiteKit.

```dockerfile
# Use a standard Python or Node image
FROM python:3.11-slim

# Install FFmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Install your dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy your app
COPY . .

CMD ["python", "agent.py"]
```

## VPS / VM

If you use a Platform-as-a-Service like **Railway** or **Render**, or a VM like **EC2**, simply install FFmpeg via the package manager.

```bash
# Ubuntu / Debian
apt-get update && apt-get install -y ffmpeg
```

## Environment Variables

Ensure your production environment has the API key set:

```bash
GEMINI_API_KEY=AIzaSy...
```

## Storage Considerations

When deployed, where do `.resource_maps` go?

*   **Ephemeral Filesystem (Docker/Cloud Run)**: Maps created during runtime will be lost when the container restarts.
*   **Solution**:
    1.  **Ingest beforehand**: Generate your JSON maps locally or in a build step, and commit them to your git repo (they are small text files!).
    2.  **Persistent Volume**: Mount a volume to `/app/.resource_maps` if you need to ingest dynamically and persist maps across restarts.
