/**
 * CiteKit JavaScript Client.
 *
 * Reads/writes resource map JSON files locally and resolves evidence
 * via modality-specific local resolvers.
 */

import { readFileSync, writeFileSync, readdirSync, existsSync, mkdirSync, statSync } from "node:fs";
import { join, basename, extname, normalize } from "node:path";
import { createHash } from "node:crypto";
import type { ResourceMap, Node, ResolvedEvidence } from "./models.js";
import { buildAddress, parseAddress } from "./address.js";

// ── Imported Mappers & Resolvers ────────────────────────────────────────

import { GeminiMapper } from "./mapper/gemini.js";
import { DocumentResolver } from "./resolvers/document.js";
import { VideoResolver } from "./resolvers/video.js";
import { ImageResolver } from "./resolvers/image.js";
import { TextResolver } from "./resolvers/text.js";
import { AudioResolver } from "./resolvers/audio.js";
import type { MapperProvider } from "./mapper/base.js";
import type { Resolver } from "./resolvers/base.js";

// ────────────────────────────────────────────────────────────────────────────

export interface CiteKitClientOptions {
    /**
     * Base directory for all CiteKit storage.
     * Useful for serverless environments (e.g. set to os.tmpdir()).
     */
    baseDir?: string;
    /** Directory where resource maps are stored. Default: ".resource_maps" */
    storageDir?: string;
    /** Directory for resolved output files. Default: ".citekit_output" */
    outputDir?: string;
    /** Gemini API Key (can also be set via env GEMINI_API_KEY) */
    apiKey?: string;
    /** Gemini Model (default: "gemini-2.0-flash") */
    model?: string;
    /** Max retries for Gemini API calls. Default: 3 */
    maxRetries?: number;
    /** Max concurrent ingestion calls. Default: 5 */
    concurrencyLimit?: number;
    /** Custom mapper implementation (e.g. for Local LLMs). */
    mapper?: MapperProvider;
}

export class CiteKitClient {
    private storageDir: string;
    private outputDir: string;
    private baseDir: string;
    private mapper: MapperProvider;
    private resolvers: Record<string, Resolver>;
    private adapters: Record<string, any> = {};
    private maxConcurrency: number;

    constructor(options: CiteKitClientOptions = {}) {
        this.baseDir = normalize(options.baseDir ?? ".");
        this.storageDir = normalize(join(this.baseDir, options.storageDir ?? ".resource_maps"));
        this.outputDir = normalize(join(this.baseDir, options.outputDir ?? ".citekit_output"));

        const apiKey = options.apiKey ?? process.env.GEMINI_API_KEY;

        // Initialize mapper: Prefer custom -> Gemini -> Mock
        if (options.mapper) {
            this.mapper = options.mapper;
        } else if (apiKey) {
            this.mapper = new GeminiMapper(apiKey, options.model, options.maxRetries);
        } else {
            // Mock mapper that throws
            this.mapper = {
                generateMap: async () => { throw new Error("GEMINI_API_KEY or custom 'mapper' required for ingestion."); }
            };
        }

        // Initialize resolvers
        this.resolvers = {
            "document": new DocumentResolver(),
            "video": new VideoResolver(),
            "audio": new AudioResolver(),
            "image": new ImageResolver(),
            "text": new TextResolver(),
        };

        // Concurrency
        this.maxConcurrency = options.concurrencyLimit ?? 5;

        // Ensure directories exist
        if (!existsSync(this.storageDir)) mkdirSync(this.storageDir, { recursive: true });
        if (!existsSync(this.outputDir)) mkdirSync(this.outputDir, { recursive: true });
    }

    // ── Map access ──────────────────────────────────────────────────────────

    /**
     * Load a previously generated map from local storage.
     */
    getMap(resourceId: string): ResourceMap {
        const mapPath = join(this.storageDir, `${resourceId}.json`);
        if (!existsSync(mapPath)) {
            throw new Error(
                `No map found for resource '${resourceId}'. Expected at: ${mapPath}`
            );
        }
        return JSON.parse(readFileSync(mapPath, "utf-8")) as ResourceMap;
    }

    /**
     * List all available resource map IDs.
     */
    listMaps(): string[] {
        if (!existsSync(this.storageDir)) return [];
        return readdirSync(this.storageDir)
            .filter((f) => f.endsWith(".json"))
            .map((f) => f.replace(/\.json$/, ""));
    }

    /**
     * Get the map as a plain object (for JSON serialization / MCP responses).
     */
    getStructure(resourceId: string): ResourceMap {
        return this.getMap(resourceId);
    }

    // ── Ingestion ───────────────────────────────────────────────────────────

    /**
     * Ingest a resource using the configured mapper.
     * 
     * Features:
     * - SHA-256 Hashing & Caching
     * - Concurrency Control
     */
    async ingest(
        resourcePath: string,
        resourceType: string,
        options?: { resourceId?: string }
    ): Promise<ResourceMap> {
        if (!existsSync(resourcePath)) {
            throw new Error(`File not found: ${resourcePath}`);
        }

        // 1. Hashing & Caching
        const fileHash = this.calculateFileHash(resourcePath);
        const cachedMap = this.findMapByHash(fileHash);

        if (cachedMap) {
            // Check if user requested specific ID? 
            // For now, return cached.
            return cachedMap;
        }

        const id = options?.resourceId || basename(resourcePath, extname(resourcePath));

        // 2. Queueing
        // Since we don't have p-limit, we use a simple internal semaphore if needed,
        // or just rely on the fact that Node is single-threaded async.
        // But to respect "queue" claim, let's use a basic lock/queue if the user calls ingest in parallel.

        // Actually, for this MVP, true semaphore in a library requires a class property.
        // Let's implement a simple acquire/release wrapper.

        const map = await this.withConcurrencyLock(async () => {
            return await this.mapper.generateMap(
                resourcePath,
                resourceType,
                id
            );
        });

        // Add metadata
        if (!map.metadata) map.metadata = {};
        map.metadata["source_hash"] = fileHash;
        map.metadata["source_size"] = statSync(resourcePath).size;

        // Save map
        const mapPath = join(this.storageDir, `${map.resource_id}.json`);
        // Ensure source_path is POSIX
        map.source_path = map.source_path.replace(/\\/g, "/");
        writeFileSync(mapPath, JSON.stringify(map, null, 2));

        return map;
    }

    // ── Power Features & Search ──────────────────────────────────────────────

    /**
     * Search across all ingested maps for nodes matching the query.
     */
    search(query: string): Array<{ resourceId: string, node: Node }> {
        const results: Array<{ resourceId: string, node: Node }> = [];
        const queryLower = query.toLowerCase();
        const maps = this.listMaps();

        for (const resourceId of maps) {
            try {
                const map = this.getMap(resourceId);
                const searchNodes = (nodes: Node[]) => {
                    for (const node of nodes) {
                        let match = false;
                        if (node.title?.toLowerCase().includes(queryLower)) match = true;
                        else if (node.summary?.toLowerCase().includes(queryLower)) match = true;

                        if (match) results.push({ resourceId, node });
                        if (node.children) searchNodes(node.children);
                    }
                };
                searchNodes(map.nodes);
            } catch (e) {
                continue;
            }
        }
        return results;
    }

    /**
     * Helper to map a standard URL or CiteKit address back to evidence.
     */
    resolveFromUrl(url: string): ResolvedEvidence | undefined {
        try {
            const { resourceId, location } = parseAddress(url);
            // We return a virtual evidence since we don't have the full Node object easily
            return {
                resource_id: resourceId,
                modality: location.modality,
                address: url,
                node: { id: "unknown", type: "section", location },
            };
        } catch (e) {
            return undefined;
        }
    }

    /**
     * Check if a node has been physically resolved/extracted recently.
     */
    isVisited(nodeId: string): boolean {
        const safeId = nodeId.replace(/\./g, "_");
        if (!existsSync(this.outputDir)) return false;
        const files = readdirSync(this.outputDir);
        return files.some(f => f.includes(`_${safeId}_`));
    }

    // ── Extendability ────────────────────────────────────────────────────────

    /**
     * Register a custom resolver for a specific modality.
     */
    registerResolver(modality: string, resolver: Resolver): void {
        this.resolvers[modality] = resolver;
    }

    /**
     * Register a custom adapter for external data sources.
     */
    registerAdapter(name: string, adapter: any): void {
        this.adapters[name] = adapter;
    }

    // ── Utilities ───────────────────────────────────────────────────────────

    private calculateFileHash(path: string): string {
        const fileBuffer = readFileSync(path);
        const hashSum = createHash("sha256");
        hashSum.update(fileBuffer);
        return hashSum.digest("hex");
    }

    private findMapByHash(hash: string): ResourceMap | undefined {
        const maps = this.listMaps();
        for (const id of maps) {
            try {
                const map = this.getMap(id);
                if (map.metadata && map.metadata["source_hash"] === hash) {
                    return map;
                }
            } catch (e) {
                continue;
            }
        }
        return undefined;
    }

    // Simple semaphore state
    private activeRequests = 0;
    private queue: Array<() => void> = [];

    private async withConcurrencyLock<T>(fn: () => Promise<T>): Promise<T> {
        if (this.activeRequests >= this.maxConcurrency) {
            await new Promise<void>(resolve => this.queue.push(resolve));
        }

        this.activeRequests++;
        try {
            return await fn();
        } finally {
            this.activeRequests--;
            if (this.queue.length > 0) {
                const next = this.queue.shift();
                next?.();
            }
        }
    }

    // ── Resolution ──────────────────────────────────────────────────────────

    /**
     * Resolve a node to evidence using the appropriate resolver.
     */
    async resolve(resourceId: string, nodeId: string, options?: { virtual?: boolean }): Promise<ResolvedEvidence> {
        const map = this.getMap(resourceId);
        const findNode = (nodes: Node[], targetId: string): Node | undefined => {
            for (const node of nodes) {
                if (node.id === targetId) return node;
                if (node.children) {
                    const found = findNode(node.children, targetId);
                    if (found) return found;
                }
            }
            return undefined;
        };

        const node = findNode(map.nodes, nodeId);

        if (!node) {
            throw new Error(`Node '${nodeId}' not found in map '${resourceId}'`);
        }

        if (options?.virtual || node.location.modality === "virtual") {
            return {
                output_path: undefined,
                modality: node.location.modality,
                address: buildAddress(resourceId, node.location),
                node,
                resource_id: resourceId
            };
        }

        const modality = node.location.modality;
        const resolver = this.resolvers[modality];

        if (!resolver) {
            throw new Error(`No resolver implementation for resource type '${modality}'`);
        }

        // Rebase source path relative to base_Dir if needed
        let sourcePath = map.source_path;
        const isAbsolute = sourcePath.startsWith("/") || sourcePath.includes(":\\");
        
        if (!isAbsolute) {
            sourcePath = join(this.baseDir, sourcePath);
        } else if (!existsSync(sourcePath)) {
            // Fallback: if absolute path doesn't exist, try relative to baseDir
            const altPath = join(this.baseDir, basename(sourcePath));
            if (existsSync(altPath)) {
                sourcePath = altPath;
            }
        }

        return resolver.resolve(
            resourceId,
            nodeId,
            sourcePath,
            node.location,
            this.outputDir,
            options
        );
    }
}
