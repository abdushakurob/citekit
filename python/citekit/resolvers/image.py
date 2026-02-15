"""Image resolver — crops a region from an image using Pillow."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from citekit.models import Node
from citekit.resolvers.base import Resolver


class ImageResolver(Resolver):
    """Crops a region from an image based on a normalized bounding box.

    The bbox is (x1, y1, x2, y2) with values normalized to 0.0-1.0,
    where (0,0) is top-left and (1,1) is bottom-right.
    """

    def resolve(self, node: Node, source_path: str) -> str:
        if node.location.bbox is None:
            raise ValueError(f"Node '{node.id}' has no bounding box in its location")

        source = Path(source_path)
        if not source.exists():
            raise FileNotFoundError(f"Source image not found: {source_path}")

        x1, y1, x2, y2 = node.location.bbox

        # Validate bbox values
        for val in (x1, y1, x2, y2):
            if not (0.0 <= val <= 1.0):
                raise ValueError(f"Bounding box values must be 0.0-1.0, got {node.location.bbox}")

        if x1 >= x2 or y1 >= y2:
            raise ValueError(f"Invalid bounding box: x1 must be < x2, y1 must be < y2. Got {node.location.bbox}")

        # Caching
        bbox_str = f"{x1:.1f}_{y1:.1f}_{x2:.1f}_{y2:.1f}"
        output_name = f"{source.stem}_crop_{bbox_str}{source.suffix}"
        output_path = self._output_dir / output_name

        if output_path.exists():
            return str(output_path)

        # Open and crop
        with Image.open(source) as img:
            width, height = img.size

            # Convert normalized coords to pixel coords
            crop_box = (
                int(x1 * width),
                int(y1 * height),
                int(x2 * width),
                int(y2 * height),
            )

            cropped = img.crop(crop_box)

            # Save cropped image
            bbox_str = f"{x1:.1f}_{y1:.1f}_{x2:.1f}_{y2:.1f}"
            output_name = f"{source.stem}_crop_{bbox_str}{source.suffix}"
            output_path = self._output_dir / output_name
            cropped.save(str(output_path))

        return str(output_path)
