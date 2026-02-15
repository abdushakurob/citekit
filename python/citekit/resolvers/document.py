"""Document resolver — extracts specific pages from a PDF into a mini-PDF."""

from __future__ import annotations

from pathlib import Path

import fitz  # PyMuPDF

from citekit.models import Node
from citekit.resolvers.base import Resolver


class DocumentResolver(Resolver):
    """Extracts specific pages from a PDF using PyMuPDF.

    Given a node with `location.pages = [12, 13]`, this resolver creates
    a new PDF containing only pages 12 and 13 from the original document.
    """

    def resolve(self, node: Node, source_path: str) -> str:
        if node.location.pages is None:
            raise ValueError(f"Node '{node.id}' has no page numbers in its location")

        source = Path(source_path)
        if not source.exists():
            raise FileNotFoundError(f"Source document not found: {source_path}")

        # Caching: Construct predicted output path
        # Note: We need to know the output name before processing.
        # Logic matches save block below:
        pages_str = "-".join(str(p) for p in node.location.pages)
        output_name = f"{source.stem}_pages_{pages_str}.pdf"
        output_path = self._output_dir / output_name

        if output_path.exists():
            return str(output_path)

        # Open source PDF
        src_doc = fitz.open(str(source))

        # Create new document with selected pages
        out_doc = fitz.open()

        for page_num in node.location.pages:
            # Pages in the map are 1-indexed, PyMuPDF is 0-indexed
            zero_indexed = page_num - 1
            if 0 <= zero_indexed < len(src_doc):
                out_doc.insert_pdf(src_doc, from_page=zero_indexed, to_page=zero_indexed)

        src_doc.close()

        if len(out_doc) == 0:
            out_doc.close()
            raise ValueError(f"No valid pages found for node '{node.id}'. "
                             f"Requested pages {node.location.pages}, document has {len(src_doc)} pages.")

        # Save mini-PDF
        pages_str = "-".join(str(p) for p in node.location.pages)
        output_name = f"{source.stem}_pages_{pages_str}.pdf"
        output_path = self._output_dir / output_name
        out_doc.save(str(output_path))
        out_doc.close()

        return str(output_path)
