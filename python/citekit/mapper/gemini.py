"""Gemini-based mapper provider for CiteKit."""

from __future__ import annotations

import json
import os
from pathlib import Path

from google import genai
from google.genai import types as genai_types

from citekit.mapper.base import MapperProvider
from citekit.models import Location, Node, ResourceMap


# ── Prompt templates ─────────────────────────────────────────────────────────

_DOCUMENT_PROMPT = """\
You are a structure analyzer. Analyze the attached document to produce a JSON map \
that identifies the key concepts, sections, definitions, examples, and diagrams.

Each node must have:
- "id": a dot-separated identifier (e.g. "chapter1.derivatives.definition")
- "title": a short human-readable title
- "type": one of "section", "definition", "example", "explanation", "diagram", "theorem", "exercise", "summary"
- "location": {{ "modality": "document", "pages": [list of 1-indexed page numbers] }}
- "summary": a 1-2 sentence summary of what this section covers

Rules:
- Be thorough — capture ALL distinct concepts, not just top-level sections.
- Page numbers are 1-indexed.
- Keep summaries concise but informative.
- IDs should be hierarchical and descriptive.

Return ONLY a JSON array of nodes. No markdown, no explanation.

Document title: {title}
"""

_IMAGE_PROMPT = """\
You are a visual structure analyzer. Given this image, identify distinct regions of interest.

Each node must have:
- "id": a descriptive dot-separated identifier
- "title": a short human-readable title
- "type": one of "diagram", "chart", "text_region", "photo", "illustration", "table", "formula"
- "location": {{ "modality": "image", "bbox": [x1, y1, x2, y2] }} where values are normalized 0.0-1.0
- "summary": brief description of what this region contains

Return ONLY a JSON array of nodes. No markdown, no explanation.
"""

_VIDEO_PROMPT = """\
You are a video structure analyzer. Given metadata about a video, identify key segments.

Video duration: {duration} seconds
Filename: {filename}

Each node must have:
- "id": a descriptive dot-separated identifier
- "title": a short human-readable title
- "type": one of "introduction", "explanation", "example", "demonstration", "summary", "transition"
- "location": {{ "modality": "video", "start": <seconds>, "end": <seconds> }}
- "summary": brief description of what this segment covers

Rules:
- Segments should be meaningful chunks, not arbitrary splits.
- start/end are in seconds.
- Cover the entire video duration.

Return ONLY a JSON array of nodes. No markdown, no explanation.
"""

_AUDIO_PROMPT = """\
You are an audio structure analyzer. Given metadata about an audio file, identify key segments.

Audio duration: {duration} seconds
Filename: {filename}

Each node must have:
- "id": a descriptive dot-separated identifier
- "title": a short human-readable title
- "type": one of "introduction", "discussion", "explanation", "example", "summary", "interlude"
- "location": {{ "modality": "audio", "start": <seconds>, "end": <seconds> }}
- "summary": brief description of what this segment covers

Return ONLY a JSON array of nodes. No markdown, no explanation.
"""


_TEXT_PROMPT = """\
You are a code/text structure analyzer. Analyze the attached text file sections.

Each node must have:
- "id": a dot-separated identifier (e.g. "MyClass.my_method" or "Installation.Requirements")
- "title": a short human-readable title
- "type": one of "class", "function", "method", "header", "section", "directive"
- "location": {{ "modality": "text", "lines": [start_line, end_line] }} (1-indexed, inclusive)
- "summary": a 1-sentence summary of what this section contains

Rules:
- Be precise with line numbers.
- Capture high-level structure (Classes, Top-level functions, Markdown headers).
- Do not map every single line of code, just the structural blocks.

Return ONLY a JSON array of nodes.
"""

class GeminiMapper(MapperProvider):
    """Mapper provider that uses Google Gemini to analyze resources.

    Args:
        api_key: Your Gemini API key.
        model: The Gemini model to use (default: "gemini-2.0-flash").
    """

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash", max_retries: int = 3):
        self._client = genai.Client(api_key=api_key)
        self._model = model
        self._max_retries = max_retries

    async def generate_map(
        self,
        resource_path: str,
        resource_type: str,
        resource_id: str | None = None,
    ) -> ResourceMap:
        path = Path(resource_path)
        if not path.exists():
            raise FileNotFoundError(f"Resource not found: {resource_path}")

        if resource_id is None:
            resource_id = path.stem

        if resource_type == "document":
            nodes = await self._map_document(path)
        elif resource_type == "image":
            nodes = await self._map_image(path)
        elif resource_type == "video":
            nodes = await self._map_video(path)
        elif resource_type == "audio":
            nodes = await self._map_audio(path)
        elif resource_type == "text":
            nodes = await self._map_text(path)
        else:
            raise ValueError(f"Unknown resource type: {resource_type}")

        return ResourceMap(
            resource_id=resource_id,
            type=resource_type,
            title=path.stem.replace("_", " ").replace("-", " ").title(),
            source_path=str(path.resolve()),
            nodes=nodes,
        )

    # ── Private methods ──────────────────────────────────────────────────────

    async def _map_document(self, path: Path) -> list[Node]:
        """Upload PDF to Gemini and ask for structure analysis."""
        prompt = _DOCUMENT_PROMPT.format(title=path.stem)
        return await self._call_gemini_with_file(path, prompt, mime_type="application/pdf")

    async def _map_image(self, path: Path) -> list[Node]:
        """Send image to Gemini for region analysis."""
        image_bytes = path.read_bytes()
        mime = _guess_image_mime(path)

        response = self._client.models.generate_content(
            model=self._model,
            contents=[
                genai_types.Content(
                    parts=[
                        genai_types.Part(text=_IMAGE_PROMPT),
                        genai_types.Part(
                            inline_data=genai_types.Blob(
                                mime_type=mime,
                                data=image_bytes,
                            )
                        ),
                    ]
                )
            ],
            config=genai_types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )

        return self._parse_nodes_response(response.text)

    async def _map_video(self, path: Path) -> list[Node]:
        """Upload video to Gemini and ask for segments."""
        duration = _get_media_duration(path)
        prompt = _VIDEO_PROMPT.format(duration=duration, filename=path.name)
        return await self._call_gemini_with_file(path, prompt, mime_type=_guess_mime_type(path))

    async def _map_audio(self, path: Path) -> list[Node]:
        """Upload audio to Gemini and ask for segments."""
        duration = _get_media_duration(path)
        prompt = _AUDIO_PROMPT.format(duration=duration, filename=path.name)
        return await self._call_gemini_with_file(path, prompt, mime_type=_guess_mime_type(path))

    async def _map_text(self, path: Path) -> list[Node]:
        """Upload text file to Gemini and ask for structure."""
        # For text files, we can just upload them as text/plain or specific mime
        # Gemini File API supports text/plain, text/markdown, text/x-python, etc.
        mime = _guess_mime_type(path)
        return await self._call_gemini_with_file(path, _TEXT_PROMPT, mime_type=mime)

    async def _call_gemini_with_file(self, path: Path, prompt: str, mime_type: str) -> list[Node]:
        """Upload file, generate content, and cleanup."""
        # 1. Upload File
        print(f"DEBUG: Uploading {path.name} to Gemini File API...")
        # Note: The new google-genai SDK uses client.files.upload
        try:
            # Sync upload for now (SDK might be sync)
            file_obj = self._client.files.upload(file=path, config={"mime_type": mime_type})
            print(f"DEBUG: Uploaded as {file_obj.name}")

            # Wait for processing if video
            if mime_type.startswith("video"):
                import time
                while file_obj.state.name == "PROCESSING":
                    print("DEBUG: Waiting for video processing...")
                    time.sleep(2)
                    file_obj = self._client.files.get(name=file_obj.name)
                
                if file_obj.state.name == "FAILED":
                    raise ValueError(f"Video processing failed: {file_obj.error.message}")

            # 2. Generate Content
            import time
            last_err = None
            for attempt in range(self._max_retries + 1):
                try:
                    response = self._client.models.generate_content(
                        model=self._model,
                        contents=[
                            genai_types.Content(
                                parts=[
                                    genai_types.Part(text=prompt),
                                    genai_types.Part(
                                        file_data=genai_types.FileData(
                                            file_uri=file_obj.uri,
                                            mime_type=file_obj.mime_type
                                        )
                                    ),
                                ]
                            )
                        ],
                        config=genai_types.GenerateContentConfig(
                            response_mime_type="application/json",
                        ),
                    )
                    return self._parse_nodes_response(response.text)
                except Exception as e:
                    last_err = e
                    if attempt < self._max_retries:
                        wait = 2 ** attempt # Exponential backoff
                        print(f"WARNING: Mapping failed (attempt {attempt+1}/{self._max_retries+1}). Retrying in {wait}s... Error: {e}")
                        time.sleep(wait)
                    else:
                        break
            
            raise last_err

        finally:
            # 3. Cleanup
            if 'file_obj' in locals() and file_obj:
                print(f"DEBUG: Deleting remote file {file_obj.name}")
                try:
                    self._client.files.delete(name=file_obj.name)
                except Exception as e:
                    print(f"WARNING: Failed to delete remote file: {e}")

    async def _call_gemini_for_nodes(self, prompt: str) -> list[Node]:
        """Send a text-only prompt to Gemini."""
        response = self._client.models.generate_content(
            model=self._model,
            contents=prompt,
            config=genai_types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        return self._parse_nodes_response(response.text)

    def _parse_nodes_response(self, text: str) -> list[Node]:
        """Parse Gemini's JSON response into Node objects."""
        import re

        # robustly extract JSON list
        cleaned = text.strip()
        
        # Try to find a JSON array pattern
        match = re.search(r"\[.*\]", cleaned, re.DOTALL)
        if match:
            cleaned = match.group(0)
        
        # Remove markdown code fences if they still exist (e.g. inside the match?) 
        # Actually regex [.*] should catch the array content locally.
        # But let's be safe against "```json [ ... ] ```" if regex picked up too much?
        # N/A, [.*] is greedy, but creates a valid bracketed scope if strict? no.
        # Simple approach: if it looks like markdown, strip it. 
        if cleaned.startswith("```"):
             # remove first line
             cleaned = cleaned.split("\n", 1)[1]
             # remove last line if it is ```
             if cleaned.rstrip().endswith("```"):
                 cleaned = cleaned.rstrip()[:-3]

        # Fix trailing commas (common LLM error)
        # remove comma before ] or }
        cleaned = re.sub(r",\s*([\]}])", r"\1", cleaned)

        # Fix missing commas between objects (common LLM error: } { -> }, {)
        cleaned = re.sub(r"}\s*{", "}, {", cleaned)

        # Attempt to repair truncated JSON (e.g. if max tokens reached)
        # Count brackets to see if we need to close them
        open_brackets = cleaned.count('[') - cleaned.count(']')
        open_braces = cleaned.count('{') - cleaned.count('}')
        
        # Simple heuristic: if we have open structures, likely truncated. 
        # Try to close specific common patterns or just append closing chars.
        if open_braces > 0:
            # Check if we are inside a string? Too complex for regex.
            # Assuming truncation happened at a safe spot or we just force close.
            # If valid JSON requires closing braces/brackets, let's add them.
            # We likely need to close the last object(s) and the main array.
            
            # Remove trailing comma if present before closing
            cleaned = cleaned.rstrip().rstrip(',')
            
            # Close braces
            cleaned += "}" * open_braces
        
        if open_brackets > 0:
             cleaned = cleaned.rstrip().rstrip(',')
             cleaned += "]" * open_brackets

        try:
            raw_nodes = json.loads(cleaned)
        except json.JSONDecodeError as e:
            # Fallback: try to just parse raw text if regex failed effectively
            try:
                raw_nodes = json.loads(text)
            except:
                print(f"DEBUG: Failed to parse JSON. Raw response preview:\n{cleaned[:500]}...[truncated]...{cleaned[-500:]}")
                raise ValueError(f"Failed to parse JSON from Gemini response: {e}") from e

        nodes = []
        for raw in raw_nodes:
            loc_data = raw.get("location", {})
            bbox = loc_data.get("bbox")
            if bbox is not None:
                bbox = tuple(bbox)

            location = Location(
                modality=loc_data.get("modality", "document"),
                pages=loc_data.get("pages"),
                lines=tuple(loc_data["lines"]) if "lines" in loc_data else None,
                start=loc_data.get("start"),
                end=loc_data.get("end"),
                bbox=bbox,
            )

            nodes.append(Node(
                id=raw["id"],
                title=raw.get("title"),
                type=raw.get("type", "section"),
                location=location,
                summary=raw.get("summary"),
            ))

        return nodes


# ── Utilities ────────────────────────────────────────────────────────────────

def _guess_image_mime(path: Path) -> str:
    """Guess MIME type from file extension."""
    ext = path.suffix.lower()
    return {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".bmp": "image/bmp",
        ".bmp": "image/bmp",
    }.get(ext, "image/png")

def _guess_mime_type(path: Path) -> str:
    """Guess MIME type for video/audio."""
    ext = path.suffix.lower()
    if ext == ".pdf": return "application/pdf"
    if ext in (".mp4", ".m4v", ".mov"): return "video/mp4"
    if ext in (".mp3", ".wav", ".aac", ".m4a"): return "audio/mp4"
    if ext in (".png", ".jpg", ".jpeg"): return "image/jpeg"
    if ext in (".txt", ".md", ".py", ".js", ".ts", ".json", ".yaml", ".yml", ".html", ".css", ".rs", ".go", ".c", ".cpp"): return "text/plain"
    return "application/octet-stream"


def _get_media_duration(path: Path) -> float:
    """Get media file duration using ffprobe."""
    import subprocess

    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "quiet",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return float(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
        # Fallback: return 0 and let the mapper handle it
        return 0.0
