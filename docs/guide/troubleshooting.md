# Troubleshooting

Common issues and how to fix them.

## Known Limitations (February 2026)

- **JavaScript CLI parity**: The Node.js package currently exposes only `citekit serve` for MCP. Commands like `ingest`, `resolve`, `list`, `check-map`, `structure`, `inspect`, and `adapt` are Python-only.

## FFmpeg Errors

### "ffprobe not found" or "ffmpeg not found"
**Cause**: FFmpeg is not installed or not in your system PATH.
**Fix**:
1. Run `ffmpeg -version` in your terminal.
2. If it fails, install FFmpeg (see [System Requirements](/guide/requirements)).
3. restart your terminal or IDE after installing.

### "Exit code 1" during resolution
**Cause**: The input file might be corrupted or the format is unsupported by your FFmpeg build.
**Fix**:
Try running the FFmpeg command manually to see the error details. CiteKit prints the command it tries to run in debug mode.

## API Errors

### "403 Forbidden" or "API Key Invalid"
**Cause**: The API key for your configured mapper is missing or invalid (for Gemini, `GEMINI_API_KEY`).
**Fix**:
Check your .env file or environment variables for the provider you use and verify key permissions.

### "429 Too Many Requests"
**Cause**: You have hit your mapper's API rate limits (RPM or RPD).
**Fix**:
- **Exponential Backoff**: CiteKit now supports automatic retries. Ensure `maxRetries` is set in your mapper.
- **Quota**: If using a free tier, wait for your quota to reset or upgrade your provider plan.
- **Concurrency**: Reduce the `concurrency_limit` in `CiteKitClient` (default: 5) to lower the parallel request volume.

### "Model not found"
**Cause**: The requested model (e.g., `gemini-1.5-flash`) is not available in your region or account tier.
**Fix**:
Try a different model name when initializing the client:
```python
client = CiteKitClient(model="gemini-1.0-pro")
```

## Ingestion Issues

### "File processing timed out"
**Cause**: Large video files take time for the mapper provider to process.
**Fix**:
CiteKit has a default timeout. You can try splitting the video into smaller chunks or retrying later.

### "Map is empty" or "No nodes found"
**Cause**: The AI couldn't find structured content, or the prompt didn't work for this specific file.
**Fix**:
*   Check if the file has meaningful content.
*   Try using a stronger model (e.g., `gemini-1.5-pro` instead of `flash`) or switch to a custom mapper.

### "Invalid Bounding Box" (Images)
**Cause**: The AI returned coordinates outside the image dimensions (e.g., negative values).
**Fix**:
*   Retry the ingestion or use a different model / custom mapper.
