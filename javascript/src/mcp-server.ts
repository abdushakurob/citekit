/**
 * CiteKit MCP Server (JavaScript/TypeScript).
 *
 * Exposes listResources, getStructure, and resolve tools via MCP.
 * Reads maps from local JSON and delegates resolution to the Python SDK.
 *
 * Run with:
 *   npx tsx src/mcp-server.ts
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
    ListToolsRequestSchema,
    CallToolRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { CiteKitClient } from "./client.js";
import { fileURLToPath } from "node:url";

function createServer(storageDir?: string, outputDir?: string): Server {
    const server = new Server(
        { name: "citekit", version: "0.1.7" },
        { capabilities: { tools: {} } }
    );

    const client = new CiteKitClient({ storageDir, outputDir });

    // ── List tools ──────────────────────────────────────────────────────────

    server.setRequestHandler(ListToolsRequestSchema, async () => ({
        tools: [
            {
                name: "listResources",
                description:
                    "List all available resource map IDs that have been ingested.",
                inputSchema: { type: "object" as const, properties: {} },
            },
            {
                name: "getStructure",
                description:
                    "Get the structured map of a resource. Returns nodes with concept/section info and physical locations.",
                inputSchema: {
                    type: "object" as const,
                    properties: {
                        resource_id: {
                            type: "string",
                            description: "The resource ID to get the structure for.",
                        },
                    },
                    required: ["resource_id"],
                },
            },
            {
                name: "resolve",
                description:
                    "Resolve a node into extracted evidence (mini-PDF, clip, or crop).",
                inputSchema: {
                    type: "object" as const,
                    properties: {
                        resource_id: {
                            type: "string",
                            description: "The resource ID.",
                        },
                        node_id: {
                            type: "string",
                            description: "The node ID to resolve.",
                        },
                        virtual: {
                            type: "boolean",
                            description: "If true, returns only metadata (timestamps/pages) without physical extraction. Useful for serverless/AI usage.",
                        },
                    },
                    required: ["resource_id", "node_id"],
                },
            },
            {
                name: "getNode",
                description:
                    "Get detailed metadata for a specific node without resolving it.",
                inputSchema: {
                    type: "object" as const,
                    properties: {
                        resource_id: {
                            type: "string",
                            description: "The resource ID.",
                        },
                        node_id: {
                            type: "string",
                            description: "The node ID.",
                        },
                    },
                    required: ["resource_id", "node_id"],
                },
            },
        ],
    }));

    // ── Call tools ──────────────────────────────────────────────────────────

    server.setRequestHandler(CallToolRequestSchema, async (request) => {
        const { name, arguments: args } = request.params;

        try {
            if (name === "listResources") {
                const resources = client.listMaps();
                return {
                    content: [
                        {
                            type: "text" as const,
                            text: JSON.stringify({ resources }, null, 2),
                        },
                    ],
                };
            }

            if (name === "getStructure") {
                const resourceId = (args as Record<string, string>).resource_id;
                const structure = client.getStructure(resourceId);
                return {
                    content: [
                        {
                            type: "text" as const,
                            text: JSON.stringify(structure, null, 2),
                        },
                    ],
                };
            }

            if (name === "getNode") {
                const { resource_id, node_id } = args as Record<string, string>;
                const structure = client.getStructure(resource_id);

                function findNode(nodes: any[], targetId: string): any {
                    for (const node of nodes) {
                        if (node.id === targetId) return node;
                        if (node.children) {
                            const found = findNode(node.children, targetId);
                            if (found) return found;
                        }
                    }
                    return null;
                }

                const node = findNode(structure.nodes, node_id);
                if (!node) {
                    throw new Error(`Node '${node_id}' not found in resource '${resource_id}'`);
                }

                return {
                    content: [
                        {
                            type: "text" as const,
                            text: JSON.stringify(node, null, 2),
                        },
                    ],
                };
            }

            if (name === "resolve") {
                const { resource_id, node_id, virtual } = args as any;
                const evidence = await client.resolve(resource_id, node_id, { virtual: !!virtual });
                return {
                    content: [
                        {
                            type: "text" as const,
                            text: JSON.stringify(evidence, null, 2),
                        },
                    ],
                };
            }

            return {
                content: [{ type: "text" as const, text: `Unknown tool: ${name}` }],
                isError: true,
            };
        } catch (error) {
            return {
                content: [
                    {
                        type: "text" as const,
                        text: `Error: ${error instanceof Error ? error.message : String(error)}`,
                    },
                ],
                isError: true,
            };
        }
    });

    return server;
}

// ── Main ────────────────────────────────────────────────────────────────────

export async function runMcpServer() {
    const server = createServer();
    const transport = new StdioServerTransport();
    await server.connect(transport);
}

// Only run if called directly
if (fileURLToPath(import.meta.url) === process.argv[1]) {
    runMcpServer().catch(console.error);
}
