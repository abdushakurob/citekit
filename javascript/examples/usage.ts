/**
 * CiteKit JavaScript SDK — Example Usage.
 *
 * Before running:
 *   1. Set GEMINI_API_KEY environment variable
 *   2. Run: npx tsx examples/usage.ts path/to/sample.pdf
 */

import { CiteKitClient } from "../src/index.js";

async function main() {
    const pdfPath = process.argv[2];
    if (!pdfPath) {
        console.log("Usage: npx tsx examples/usage.ts <path-to-pdf>");
        process.exit(1);
    }

    console.log(`📄 Resource: ${pdfPath}\n`);

    const client = new CiteKitClient();

    // ── Step 1: Ingest ────────────────────────────────────────────────────

    console.log("🔍 Ingesting resource...");
    const resourceMap = await client.ingest(pdfPath, "document");

    console.log(`✅ Map generated: ${resourceMap.resource_id}`);
    console.log(`   Title: ${resourceMap.title}`);
    console.log(`   Nodes: ${resourceMap.nodes.length}\n`);

    // ── Step 2: Inspect ───────────────────────────────────────────────────

    console.log("📋 Resource Map:");
    console.log("-".repeat(60));
    for (const node of resourceMap.nodes) {
        console.log(`  [${node.type}] ${node.id}`);
        console.log(`    Title: ${node.title}`);
        console.log(`    Pages: ${JSON.stringify(node.location.pages ?? [])}`);
        if (node.summary) console.log(`    Summary: ${node.summary}`);
        console.log();
    }

    // ── Step 3: Resolve ───────────────────────────────────────────────────

    if (resourceMap.nodes.length > 0) {
        const firstNode = resourceMap.nodes[0];
        console.log(`📎 Resolving node: ${firstNode.id}`);

        const evidence = await client.resolve(resourceMap.resource_id, firstNode.id);
        console.log(`  ✅ Output: ${evidence.output_path}`);
        console.log(`  📍 Address: ${evidence.address}`);
        console.log(`  📦 Modality: ${evidence.modality}`);
    }

    // ── Step 4: List maps ─────────────────────────────────────────────────

    console.log(`\n💾 Stored maps: ${JSON.stringify(client.listMaps())}`);
}

main().catch(console.error);
