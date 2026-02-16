# System Requirements

CiteKit is a hybrid cloud/local system. The "heavy lifting" of understanding content happens in the cloud (via Gemini API), but the "heavy lifting" of extracting content happens **locally on your machine**.

## Supported Operating Systems

CiteKit is tested and supported on:

*   **macOS**: 12+ (Apple Silicon & Intel)
*   **Windows**: 10, 11 (PowerShell or WSL2 recommended)
*   **Linux**: Ubuntu 20.04+, Debian 11+, Alpine 3.14+

## Language Runtimes

### Python SDK
*   **Python 3.10+** (Required for modern type hinting features)

### JavaScript SDK
*   **Node.js 18+** (Required for native `fetch` and `crypto` APIs)

## External Dependencies

### FFmpeg (Optional)

**Why is it needed?**
CiteKit uses FFmpeg to slice video and audio files locally (**Physical Resolution**). Without it, you cannot resolve video/audio into new clip files.

**When is it NOT needed?**
-   **Virtual Resolution**: If you only need timestamps/metadata.
-   **Modality**: If you only use PDFs, Images, or Text/Code.
-   **Serverless**: Use [Virtual Mode](/guide/concepts/virtual-mode) for zero-binary deployments.

**Requirement:**
*   **FFmpeg 4.0+**
*   Must be available in the system `PATH`.

**How to verify:**
```bash
ffmpeg -version
```

### PDF Tools

*   **Python**: `pypdf` is installed automatically.
*   **Node.js**: `pdf-lib` is installed automatically.

## Storage

CiteKit creates two local directories by default:

1.  **`.resource_maps/`**: Stores JSON maps. Tiny (few KB per file).
2.  **`.citekit_output/`**: Stores extracted clips/PDFs.
    *   *Best Practice*: Configure your agent to delete these files after use if disk space is a concern.
