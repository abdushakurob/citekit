"""Example usage of CiteKit Python SDK.

Before running:
    1. pip install -e .
    2. Set your Gemini API key: export GEMINI_API_KEY=your_key_here
    3. Place a sample PDF in the same directory or adjust the path below.

Usage:
    python examples/usage.py path/to/sample.pdf
"""

import asyncio
import json
import os
import sys

from citekit import CiteKitClient, GeminiMapper


async def main():
    # ── Configuration ────────────────────────────────────────────────────────

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: Set GEMINI_API_KEY environment variable.")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Usage: python examples/usage.py <path-to-pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    print(f"📄 Resource: {pdf_path}\n")

    # ── Step 1: Initialize ───────────────────────────────────────────────────

    mapper = GeminiMapper(api_key=api_key, model="gemini-2.0-flash")
    client = CiteKitClient(mapper=mapper)

    # ── Step 2: Ingest ───────────────────────────────────────────────────────

    print("🔍 Ingesting resource...")
    resource_map = await client.ingest(pdf_path, "document")

    print(f"✅ Map generated: {resource_map.resource_id}")
    print(f"   Title: {resource_map.title}")
    print(f"   Nodes: {len(resource_map.nodes)}\n")

    # ── Step 3: Inspect the map ──────────────────────────────────────────────

    print("📋 Resource Map:")
    print("-" * 60)
    for node in resource_map.nodes:
        pages = node.location.pages or []
        print(f"  [{node.type}] {node.id}")
        print(f"    Title: {node.title}")
        print(f"    Pages: {pages}")
        if node.summary:
            print(f"    Summary: {node.summary}")
        print()

    # ── Step 4: Resolve the first node ───────────────────────────────────────

    if resource_map.nodes:
        first_node = resource_map.nodes[0]
        print(f"📎 Resolving node: {first_node.id}")

        evidence = client.resolve(resource_map.resource_id, first_node.id)

        print(f"  ✅ Output: {evidence.output_path}")
        print(f"  📍 Address: {evidence.address}")
        print(f"  📦 Modality: {evidence.modality}")

    # ── Step 5: Show that maps persist ───────────────────────────────────────

    print(f"\n💾 Stored maps: {client.list_maps()}")


if __name__ == "__main__":
    asyncio.run(main())
