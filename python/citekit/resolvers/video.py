"""Video resolver — extracts a clip from a video using ffmpeg."""

from __future__ import annotations

import subprocess
from pathlib import Path

from citekit.models import Node
from citekit.resolvers.base import Resolver


class VideoResolver(Resolver):
    """Extracts a time-based clip from a video using ffmpeg.

    Uses stream copy (-c copy) to avoid re-encoding for fast extraction.
    Falls back to re-encoding if stream copy fails.
    """

    def resolve(self, node: Node, source_path: str) -> str:
        if node.location.start is None or node.location.end is None:
            raise ValueError(f"Node '{node.id}' is missing start/end timestamps")

        source = Path(source_path)
        if not source.exists():
            raise FileNotFoundError(f"Source video not found: {source_path}")

        start = node.location.start
        duration = node.location.end - node.location.start

        if duration <= 0:
            raise ValueError(f"Invalid time range: start={start}, end={node.location.end}")

        # Output filename
        start_str = f"{int(start)}s"
        end_str = f"{int(node.location.end)}s"
        output_name = f"{source.stem}_clip_{start_str}-{end_str}{source.suffix}"
        output_path = self._output_dir / output_name

        # Try stream copy first (fast, no re-encoding)
        try:
            self._extract_clip(source, output_path, start, duration, copy=True)
        except subprocess.CalledProcessError:
            # Fall back to re-encoding
            self._extract_clip(source, output_path, start, duration, copy=False)

        return str(output_path)

    def _extract_clip(
        self, source: Path, output: Path, start: float, duration: float, copy: bool
    ) -> None:
        """Run ffmpeg to extract a clip."""
        cmd = [
            "ffmpeg",
            "-y",  # Overwrite output
            "-ss", str(start),
            "-i", str(source),
            "-t", str(duration),
        ]

        if copy:
            cmd.extend(["-c", "copy"])

        cmd.append(str(output))

        subprocess.run(
            cmd,
            capture_output=True,
            check=True,
        )
