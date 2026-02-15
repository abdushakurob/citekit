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

function createServer(storageDir?: string, outputDir?: string): Server {
    const server = new Server(
        { name: "citekit", version: "0.1.0" },
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

            if (name === "resolve") {
                const { resource_id, node_id } = args as Record<string, string>;
                const evidence = client.resolve(resource_id, node_id);
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
if (import.meta.url === `file://${process.argv[1]}`) {
    runMcpServer().catch(console.error);
}
