# Troubleshooting

Common issues and how to fix them.

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
**Cause**: `GEMINI_API_KEY` is missing or invalid.
**Fix**:
Check your .env file or environment variables. Ensure the key has permissions for "Generative Language API".

### "429 Too Many Requests"
**Cause**: You have hit the Gemini API rate limits (RPM or RPD).
**Fix**:
- **Exponential Backoff**: CiteKit now supports automatic retries. Ensure `maxRetries` is set in your mapper.
- **Pay-as-you-go**: If using the Free Tier, wait for your quota to reset or upgrade in Google AI Studio.
- **Concurrency**: Reduce the `concurrency_limit` in `CiteKitClient` (default: 5) to lower the parallel request volume.

### "Model not found"
**Cause**: The requested model (e.g., `gemini-1.5-flash`) is not available in your region or account tier.
**Fix**:
Try a different model name when initializing the client:
```python
client = CiteKitClient(model_name="gemini-1.0-pro")
```

## Ingestion Issues

### "File processing timed out"
**Cause**: Large video files take time for Google to process.
**Fix**:
CiteKit has a default timeout. You can try splitting the video into smaller chunks or retrying later.

### "Map is empty" or "No nodes found"
**Cause**: The AI couldn't find structured content, or the prompt didn't work for this specific file.
**Fix**:
*   Check if the file has meaningful content.
*   Try using a stronger model (`gemini-1.5-pro` instead of `flash`).

### "Invalid Bounding Box" (Images)
**Cause**: The AI hallucinated coordinates outside the image dimensions (e.g., negative values).
**Fix**:
*   This is rare with Gemini 1.5, but can happen. Retry the ingestion or use a different model.
