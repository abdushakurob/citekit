/* research_agent.js */
import 'dotenv/config';
import fs from 'node:fs';
import path from 'node:path';
import { CiteKitClient } from 'citekit';

// CiteKit acts as the "Optical" layer for our researcher
const client = new CiteKitClient({
    outputDir: 'research_evidence'
});

async function runResearchTask() {
    const paperPath = './papers/sample_paper.pdf';
    
    if (!fs.existsSync(paperPath)) {
        console.error('[ERROR] Sample paper not found. Please add a PDF to ./papers/sample_paper.pdf');
        process.exit(1);
    }

    console.log(`[INFO] Inspecting Paper: ${path.basename(paperPath)}`);

    // STEP 1: Discovery (Ingestion)
    // The file is sent to the mapper service (Gemini by default) ONCE to generate the map.
    // This is the only time the file leaves your local machine.
    const map = await client.ingest(paperPath, 'document');
    
    console.log(`[INFO] Paper mapped with ${map.nodes.length} structural nodes`);

    // STEP 2: Intent Analysis
    // We want to find where the experimental methodology is.
    // In a real agent, the LLM would pick these node IDs.
    const methodologyNodes = map.nodes.filter(node => 
        node.id.includes('method') || 
        node.id.includes('experiment') ||
        (node.summary && (
            node.summary.toLowerCase().includes('method') || 
            node.summary.toLowerCase().includes('experiment')
        ))
    );

    if (methodologyNodes.length === 0) {
        console.log('[INFO] No methodology sections found. Listing all nodes:');
        map.nodes.forEach(node => {
            console.log(`  - ${node.id}: ${node.title || 'Untitled'}`);
            if (node.summary) {
                console.log(`    Summary: ${node.summary.substring(0, 100)}...`);
            }
        });
        return;
    }

    // STEP 3: Contextual Retrieval & Evidence Extraction
    for (const node of methodologyNodes) {
        console.log(`[INFO] Orchestrating Context: "${node.title || node.id}"`);
        
        // This extracts the specific pages as a high-fidelity PDF slice
        const evidence = await client.resolve(map.resource_id, node.id);
        
        console.log(`[SUCCESS] Evidence extracted to: ${evidence.output_path}`);
    }
}

runResearchTask().catch(console.error);
