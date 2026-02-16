"""Address parser and builder for CiteKit URI-style addresses.

Formats:
    doc://resource_id#pages=3-5
    video://resource_id#t=192-230
    audio://resource_id#t=60-120
    image://resource_id#bbox=0.2,0.3,0.8,0.7
"""

from __future__ import annotations

import re
from urllib.parse import urlparse, parse_qs

from citekit.models import Location

# Scheme → modality mapping
_SCHEME_TO_MODALITY = {
    "doc": "document",
    "video": "video",
    "audio": "audio",
    "image": "image",
    "text": "text",
    "virtual": "virtual",
}

_MODALITY_TO_SCHEME = {v: k for k, v in _SCHEME_TO_MODALITY.items()}


def parse_address(address: str) -> tuple[str, Location]:
    """Parse a CiteKit address into (resource_id, Location).

    Examples:
        >>> parse_address("doc://calculus_book#pages=12-13")
        ('calculus_book', Location(modality='document', pages=[12, 13]))

        >>> parse_address("video://lecture1#t=192-230")
        ('lecture1', Location(modality='video', start=192.0, end=230.0))
        
        >>> parse_address("text://code#lines=10-20")
        ('code', Location(modality='text', lines=(10, 20)))

        >>> parse_address("image://diagram#bbox=0.2,0.3,0.8,0.7")
        ('diagram', Location(modality='image', bbox=(0.2, 0.3, 0.8, 0.7)))
    """
    # Parse scheme manually since urllib doesn't handle custom schemes well
    match = re.match(r"^(\w+)://([^#]+)(?:#(.+))?$", address)
    if not match:
        raise ValueError(f"Invalid CiteKit address: {address}")

    scheme, resource_id, fragment = match.group(1), match.group(2), match.group(3)

    if scheme not in _SCHEME_TO_MODALITY:
        raise ValueError(f"Unknown scheme '{scheme}'. Expected one of: {list(_SCHEME_TO_MODALITY.keys())}")

    modality = _SCHEME_TO_MODALITY[scheme]

    if scheme == "virtual":
        return resource_id, Location(
            modality="virtual",
            virtual_address=address,
        )

    # Parse fragment parameters
    pages = None
    start = None
    end = None
    bbox = None
    lines = None

    if fragment:
        params = dict(part.split("=", 1) for part in fragment.split("&") if "=" in part)

        if "pages" in params:
            page_str = params["pages"]
            if "-" in page_str:
                p_start, p_end = page_str.split("-", 1)
                pages = list(range(int(p_start), int(p_end) + 1))
            else:
                pages = [int(p) for p in page_str.split(",")]

        if "lines" in params:
            lines_str = params["lines"]
            if "-" in lines_str:
                l_start, l_end = lines_str.split("-", 1)
                lines = (int(l_start), int(l_end))
            elif "," in lines_str:
                # Fallback if someone uses comma, but lines is usually a range tuple
                parts = lines_str.split(",")
                if len(parts) >= 2:
                    lines = (int(parts[0]), int(parts[-1]))
                else:
                    lines = (int(parts[0]), int(parts[0]))

        if "t" in params:
            time_str = params["t"]
            if "-" in time_str:
                t_start, t_end = time_str.split("-", 1)
                start = _parse_time(t_start)
                end = _parse_time(t_end)

        if "bbox" in params:
            parts = params["bbox"].split(",")
            if len(parts) != 4:
                raise ValueError(f"bbox must have 4 values, got {len(parts)}")
            bbox = tuple(float(p) for p in parts)

    return resource_id, Location(
        modality=modality,
        pages=pages,
        start=start,
        end=end,
        bbox=bbox,
        lines=lines,
    )


def build_address(resource_id: str, location: Location) -> str:
    """Build a CiteKit address from a resource ID and location.

    Examples:
        >>> build_address("book", Location(modality="document", pages=[3, 4, 5]))
        'doc://book#pages=3-5'

        >>> build_address("lecture", Location(modality="video", start=192.0, end=230.0))
        'video://lecture#t=192-230'
    """
    scheme = _MODALITY_TO_SCHEME.get(location.modality)
    if not scheme:
        raise ValueError(f"Unknown modality: {location.modality}")

    if location.modality == "virtual":
        return location.virtual_address or f"virtual://{resource_id}"

    fragment_parts = []

    if location.pages is not None:
        if len(location.pages) == 0:
            raise ValueError("Pages list cannot be empty")
        pages_sorted = sorted(location.pages)
        # Check if pages are consecutive for range notation
        if pages_sorted == list(range(pages_sorted[0], pages_sorted[-1] + 1)):
            fragment_parts.append(f"pages={pages_sorted[0]}-{pages_sorted[-1]}")
        else:
            fragment_parts.append(f"pages={','.join(str(p) for p in pages_sorted)}")

    if location.lines is not None:
        start_line, end_line = location.lines
        fragment_parts.append(f"lines={start_line}-{end_line}")

    if location.start is not None and location.end is not None:
        start_str = _format_time(location.start)
        end_str = _format_time(location.end)
        fragment_parts.append(f"t={start_str}-{end_str}")

    if location.bbox is not None:
        bbox_str = ",".join(f"{v:g}" for v in location.bbox)
        fragment_parts.append(f"bbox={bbox_str}")

    fragment = "&".join(fragment_parts)
    if fragment:
        return f"{scheme}://{resource_id}#{fragment}"
    return f"{scheme}://{resource_id}"


def _parse_time(time_str: str) -> float:
    """Parse a time string to seconds. Supports seconds or HH:MM:SS format."""
    time_str = time_str.strip()

    # HH:MM:SS or MM:SS format
    if ":" in time_str:
        parts = time_str.split(":")
        if len(parts) == 3:
            h, m, s = parts
            return int(h) * 3600 + int(m) * 60 + float(s)
        elif len(parts) == 2:
            m, s = parts
            return int(m) * 60 + float(s)

    return float(time_str)


def _format_time(seconds: float) -> str:
    """Format seconds as a compact time string."""
    if seconds == int(seconds):
        seconds = int(seconds)

    # Use HH:MM:SS for large values
    if isinstance(seconds, int) and seconds >= 3600:
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"
    elif isinstance(seconds, int) and seconds >= 60:
        m = seconds // 60
        s = seconds % 60
        return f"{m:02d}:{s:02d}"

    return str(seconds)
