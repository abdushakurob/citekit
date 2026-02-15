/**
 * CiteKit JavaScript Client.
 *
 * Reads/writes resource map JSON files locally and calls the Python
 * resolver backend for resolution (since resolvers are Python-based).
 */

import { readFileSync, writeFileSync, readdirSync, existsSync, mkdirSync } from "node:fs";
import { join, basename, extname } from "node:path";
import { execSync } from "node:child_process";
import { createHash } from "node:crypto";
import type { ResourceMap, Node, ResolvedEvidence } from "./models.js";
import { buildAddress } from "./address.js";

// ── Imported Mappers & Resolvers ────────────────────────────────────────

import { GeminiMapper } from "./mapper/gemini.js";
import { DocumentResolver } from "./resolvers/document.js";
import { VideoResolver } from "./resolvers/video.js";
import { ImageResolver } from "./resolvers/image.js";
import type { MapperProvider } from "./mapper/base.js";
import type { Resolver } from "./resolvers/base.js";

// ────────────────────────────────────────────────────────────────────────────

export interface CiteKitClientOptions {
    /** Directory where resource maps are stored. Default: ".resource_maps" */
    storageDir?: string;
    /** Directory for resolved output files. Default: ".citekit_output" */
    outputDir?: string;
    /** Gemini API Key (can also be set via env GEMINI_API_KEY) */
    apiKey?: string;
    /** Gemini Model (default: "gemini-2.0-flash") */
    model?: string;
}

export class CiteKitClient {
    private storageDir: string;
    private outputDir: string;
    private mapper: MapperProvider;
    private resolvers: Record<string, Resolver>;

    constructor(options: CiteKitClientOptions = {}) {
        this.storageDir = options.storageDir ?? ".resource_maps";
        this.outputDir = options.outputDir ?? ".citekit_output";

        const apiKey = options.apiKey ?? process.env.GEMINI_API_KEY;
        if (!apiKey) {
            // We allow client init without key, but ingest will fail if we don't have it eventually.
            // For now, let's just warn or let the mapper throw.
            // Actually, the mapper constructor needs it.
            // If unavailable, we can delay mapper init? Or throw?
            // Let's assume user must provide it if they want to ingest.
            // But if they only want resolve(), they might not need it?
            // Resolution logic doesn't need Gemini.
            // So we should lazily init mapper or allow null.
        }

        // Initialize mapper
        // Note: For this MVP port, we assume GeminiMapper is the default.
        if (apiKey) {
            this.mapper = new GeminiMapper(apiKey, options.model);
        } else {
            // Mock mapper that throws
            this.mapper = {
                generateMap: async () => { throw new Error("GEMINI_API_KEY required for ingestion."); }
            };
        }

        // Initialize resolvers
        this.resolvers = {
            "document": new DocumentResolver(),
            "video": new VideoResolver(),
            "image": new ImageResolver(),
            // Audio uses VideoResolver logic mostly, but we can reuse or just alias?
            // "audio" -> Generic A/V resolver?
            // "audio": new VideoResolver(), // ffmpeg handles both
        };

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

        // Save map
        const mapPath = join(this.storageDir, `${map.resource_id}.json`);
        writeFileSync(mapPath, JSON.stringify(map, null, 2));

        return map;
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
    private maxConcurrency = 5;
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
    async resolve(resourceId: string, nodeId: string): Promise<ResolvedEvidence> {
        const map = this.getMap(resourceId);
        const node = map.nodes.find((n) => n.id === nodeId);

        if (!node) {
            throw new Error(`Node '${nodeId}' not found in map '${resourceId}'`);
        }

        const type = map.type; // document, video, etc.
        const resolver = this.resolvers[type];

        if (!resolver) {
            // Check if we can fallback?
            // For now, if no resolver, failure.
            // Maybe handle "audio" with video resolver?
            if (type === "audio" && this.resolvers["video"]) {
                return this.resolvers["video"].resolve(resourceId, nodeId, map.source_path, node.location, this.outputDir);
            }
            throw new Error(`No resolver implementation for resource type '${type}'`);
        }

        return resolver.resolve(
            resourceId,
            nodeId,
            map.source_path,
            node.location,
            this.outputDir
        );
    }
}
