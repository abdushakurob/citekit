# Deployment Guide

Deploying an application that uses CiteKit requires careful consideration of the **Runtime Environment**, specifically regarding FFmpeg availability.

## The Serverless Challenge

Most "Serverless" environments (AWS Lambda, Vercel Functions, Netlify Functions) have limitations:
1.  **No FFmpeg**: Not installed by default.
2.  **Timeouts**: Execution limits (10-60s) may interrupt video processing.
3.  **Ephemeral Storage**: Limited disk space.

### Compatibility Table

| Platform | Ingestion (Gemini) | Resolution (FFmpeg) |
| :--- | :--- | :--- |
| **Vercel / Netlify** | Yes | No (usually) |
| **AWS Lambda** | Yes | Requires Layer |
| **Docker / VPS** | Yes | Yes |

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
