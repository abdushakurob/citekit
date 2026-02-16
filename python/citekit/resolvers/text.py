from __future__ import annotations

import os

from citekit.models import Node
from citekit.resolvers.base import Resolver


class TextResolver(Resolver):
    """Resolves text file locations by extracting line ranges."""

    def __init__(self, output_dir: str):
        super().__init__(output_dir)

    def resolve(self, node: Node, source_path: str) -> str:
        """Extract lines from a text file."""
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source file not found: {source_path}")

        if node.location.lines is None:
            raise ValueError(f"Node '{node.id}' has no line range defined.")

        start_line, end_line = node.location.lines
        # Convert to 0-indexed for python list slicing
        # 1-indexed inclusive -> 0-indexed exclusive
        # e.g. lines 1-3 -> [0, 1, 2] -> split[0:3]
        start_idx = max(0, start_line - 1)
        end_idx = end_line

        with open(source_path, "r", encoding="utf-8") as f:
            all_lines = f.readlines()

        if start_idx >= len(all_lines):
            raise ValueError(f"Start line {start_line} is beyond file length {len(all_lines)}.")

        extracted_lines = all_lines[start_idx:end_idx]
        content = "".join(extracted_lines)

        # Output file
        basename = os.path.basename(source_path)
        name, ext = os.path.splitext(basename)
        safe_id = node.id.replace(".", "_")
        output_filename = f"{name}_{safe_id}_lines_{start_line}-{end_line}{ext}"
        output_path = self._output_dir / output_filename

        if output_path.exists():
            return str(output_path)

        with open(output_path, "w", encoding="utf-8") as out:
            out.write(content)

        return str(output_path)
