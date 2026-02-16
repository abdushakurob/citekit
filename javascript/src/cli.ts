#!/usr/bin/env node
import { Command } from 'commander';
import { CiteKitClient } from './client.js';
import { existsSync, readFileSync } from 'node:fs';
import { extname, basename } from 'node:path';

const program = new Command();

program
    .name('citekit')
    .description('CiteKit CLI - Local AI Resource Mapper & Resolver')
    .version('0.1.8');

// ── Ingest Command ──────────────────────────────────────────────────────────

program.command('ingest')
    .description('Ingest a file and generate a resource map')
    .argument('<path>', 'Path to the file to ingest')
    .option('-t, --type <type>', 'Resource type (document, video, audio, image, text). If omitted, inferred from extension.')
    .option('-c, --concurrency <number>', 'Max parallel mapper calls', '5')
    .option('-r, --retries <number>', 'Max retries for API failures', '3')
    .action(async (path: string, options: any) => {
        if (!existsSync(path)) {
            console.error('[ERROR] File not found:', path);
            process.exit(1);
        }

        let type = options.type;
        if (!type) {
            const ext = extname(path).toLowerCase();
            const typeMap: Record<string, string> = {
                '.pdf': 'document',
                '.txt': 'text', '.md': 'text', '.py': 'text', '.js': 'text', '.ts': 'text',
                '.json': 'text', '.yaml': 'text', '.yml': 'text', '.rst': 'text',
                '.mp4': 'video', '.mov': 'video', '.avi': 'video', '.mkv': 'video',
                '.mp3': 'audio', '.wav': 'audio', '.m4a': 'audio',
                '.png': 'image', '.jpg': 'image', '.jpeg': 'image', '.webp': 'image'
            };
            type = typeMap[ext];
            if (!type) {
                console.error(`[!] Could not infer type from extension '${ext}'. Please specify --type.`);
                process.exit(1);
            }
        }

        console.log(`[INFO] Ingesting ${path} as '${type}'...`);

        try {
            const client = new CiteKitClient({
                concurrencyLimit: parseInt(options.concurrency),
                maxRetries: parseInt(options.retries)
            });

            const resourceMap = await client.ingest(path, type);
            console.log(`[SUCCESS] Map generated: ${resourceMap.resource_id}`);
            console.log(`   Title: ${resourceMap.title}`);
            console.log(`   Nodes: ${resourceMap.nodes.length}`);
        } catch (error: any) {
            console.error('[ERROR]', error.message);
            process.exit(1);
        }
    });

// ── Resolve Command ─────────────────────────────────────────────────────────

program.command('resolve')
    .description('Resolve a node ID to its value (file chunk)')
    .argument('<node_id>', 'Node ID to resolve')
    .option('-res, --resource <id>', 'Resource ID (optional if node_id is unique)')
    .option('--virtual', 'Virtual resolution (metadata only)')
    .action(async (nodeId: string, options: any) => {
        console.log(`[RESOLVING] Node: ${nodeId}`);

        try {
            const client = new CiteKitClient();

            let rid: string;
            let nid: string;

            if (nodeId.includes('.') && !options.resource) {
                [rid, nid] = nodeId.split('.', 2);
            } else {
                rid = options.resource;
                nid = nodeId;
            }

            if (!rid) {
                console.error('[!] Resource ID missing. Use --resource or rid.nid format.');
                process.exit(1);
            }

            const evidence = await client.resolve(rid, nid, { virtual: options.virtual });

            if (options.virtual) {
                console.log('[SUCCESS] Virtual resolution successful.');
            } else {
                console.log(`[SUCCESS] Output: ${evidence.output_path}`);
            }
            console.log(`   Modality: ${evidence.modality}`);
            console.log(`   Address: ${evidence.address}`);
        } catch (error: any) {
            console.error('[ERROR]', error.message);
            process.exit(1);
        }
    });

// ── Structure Command ───────────────────────────────────────────────────────

program.command('structure')
    .description('Get the JSON structure (map) for a resource ID')
    .argument('<resource_id>', 'Resource ID')
    .action(async (resourceId: string) => {
        try {
            const client = new CiteKitClient();
            const resourceMap = client.getMap(resourceId);
            console.log(JSON.stringify(resourceMap, null, 2));
        } catch (error: any) {
            console.error('[ERROR]', error.message);
            process.exit(1);
        }
    });

// ── List Command ────────────────────────────────────────────────────────────

program.command('list')
    .description('List ingested resources or nodes within a resource')
    .argument('[resource_id]', 'Optional resource ID to list nodes')
    .action(async (resourceId?: string) => {
        try {
            const client = new CiteKitClient();

            if (resourceId) {
                // List nodes for specific resource
                const resourceMap = client.getMap(resourceId);
                console.log(`[INFO] Nodes in '${resourceId}':`);

                const printNodes = (nodes: any[], prefix = '') => {
                    for (const node of nodes) {
                        console.log(`${prefix}- ${node.id} (${node.type}): ${node.title}`);
                        if (node.children && node.children.length > 0) {
                            printNodes(node.children, prefix + '  ');
                        }
                    }
                };

                printNodes(resourceMap.nodes);
            } else {
                // List all resources
                const maps = client.listMaps();
                if (maps.length === 0) {
                    console.log('No resources found.');
                    return;
                }

                console.log(`found ${maps.length} resources:`);
                for (const id of maps) {
                    try {
                        const resourceMap = client.getMap(id);
                        console.log(` - ${resourceMap.resource_id} (${resourceMap.type}): ${resourceMap.title}`);
                    } catch {
                        console.log(` - ${id} (corrupt)`);
                    }
                }
            }
        } catch (error: any) {
            console.error('[ERROR]', error.message);
            process.exit(1);
        }
    });

// ── Check-Map Command ───────────────────────────────────────────────────────

program.command('check-map')
    .description('Validate a ResourceMap JSON file')
    .argument('<path>', 'Path to the JSON file')
    .action(async (path: string) => {
        if (!existsSync(path)) {
            console.error('[ERROR] File not found:', path);
            process.exit(1);
        }

        try {
            const content = readFileSync(path, 'utf-8');
            const data = JSON.parse(content);

            // Basic validation
            if (!data.resource_id || !data.type || !data.nodes) {
                console.error('[ERROR] Invalid ResourceMap: missing required fields (resource_id, type, nodes)');
                process.exit(1);
            }

            console.log('[SUCCESS] ResourceMap is valid');
            console.log(`   Resource ID: ${data.resource_id}`);
            console.log(`   Type: ${data.type}`);
            console.log(`   Nodes: ${data.nodes.length}`);
        } catch (error: any) {
            console.error('[ERROR]', error.message);
            process.exit(1);
        }
    });

// ── Inspect Command ─────────────────────────────────────────────────────────

program.command('inspect')
    .description("Inspect a node's metadata without resolving")
    .argument('<node_id>', 'Node ID to inspect')
    .option('-res, --resource <id>', 'Resource ID (optional if node_id is unique)')
    .action(async (nodeId: string, options: any) => {
        try {
            const client = new CiteKitClient();

            let rid: string;
            let nid: string;

            if (nodeId.includes('.') && !options.resource) {
                [rid, nid] = nodeId.split('.', 2);
            } else {
                rid = options.resource;
                nid = nodeId;
            }

            if (!rid) {
                console.error('[!] Resource ID missing. Use --resource or rid.nid format.');
                process.exit(1);
            }

            const resourceMap = client.getMap(rid);
            const findNode = (nodes: any[], targetId: string): any => {
                for (const node of nodes) {
                    if (node.id === targetId) return node;
                    if (node.children) {
                        const found = findNode(node.children, targetId);
                        if (found) return found;
                    }
                }
                return null;
            };

            const node = findNode(resourceMap.nodes, nid);
            if (!node) {
                console.error(`[ERROR] Node '${nid}' not found in resource '${rid}'`);
                process.exit(1);
            }

            console.log(`[INFO] Node: ${node.id}`);
            console.log(`   Title: ${node.title}`);
            console.log(`   Type: ${node.type}`);
            console.log(`   Modality: ${node.location.modality}`);
            if (node.summary) {
                console.log(`   Summary: ${node.summary}`);
            }
        } catch (error: any) {
            console.error('[ERROR]', error.message);
            process.exit(1);
        }
    });

// ── Adapt Command ───────────────────────────────────────────────────────────

program.command('adapt')
    .description('Adapt an external map format to CiteKit ResourceMap')
    .argument('<path>', 'Path to the external map JSON file')
    .option('-f, --format <format>', 'Source format (graphrag, llamaindex)', 'graphrag')
    .action(async (path: string, options: any) => {
        console.log(`[INFO] Adapting ${options.format} map from ${path}...`);
        console.error('[ERROR] Adapt command not yet implemented in JavaScript CLI');
        console.error('[INFO] Use the Python CLI: python -m citekit.cli adapt');
        process.exit(1);
    });

// ── Serve Command ───────────────────────────────────────────────────────────

program.command('serve')
    .description('Start the MCP server (stdio mode) for AI agents')
    .action(async () => {
        const { runMcpServer } = await import('./mcp-server.js');
        await runMcpServer();
    });

program.parse(process.argv);
