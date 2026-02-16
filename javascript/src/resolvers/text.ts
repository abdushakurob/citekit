import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { join, basename, extname } from "node:path";
import type { Resolver } from "./base.js";
import type { Location, ResolvedEvidence } from "../models.js";
import { buildAddress } from "../address.js";

export class TextResolver implements Resolver {
    async resolve(
        resourceId: string,
        nodeId: string,
        sourcePath: string,
        location: Location,
        outputDir: string,
        options?: { virtual?: boolean }
    ): Promise<ResolvedEvidence> {
        // 1. Virtual Resolution
        if (options?.virtual) {
            return {
                resource_id: resourceId,
                modality: "text",
                address: buildAddress(resourceId, location),
                node: {
                    id: nodeId,
                    title: nodeId, // We don't have title here without the Map node object, but that's ok for evidence return
                    type: "section",
                    location: location
                }
            };
        }

        // 2. Physical Resolution
        if (!existsSync(sourcePath)) {
            throw new Error(`Source file not found: ${sourcePath}`);
        }

        if (!location.lines) {
            throw new Error(`Node '${nodeId}' has no line range defined.`);
        }

        const [startLine, endLine] = location.lines;

        // Read file
        const fileContent = readFileSync(sourcePath, "utf-8");
        const allLines = fileContent.split(/\r?\n/);

        // 1-indexed inclusive -> 0-indexed exclusive
        // Lines 1-2 means: index 0 and 1.
        const startIdx = Math.max(0, startLine - 1);
        const endIdx = endLine; // Slice is exclusive at end, so this works nicely. 

        if (startIdx >= allLines.length) {
            throw new Error(`Start line ${startLine} is beyond file length ${allLines.length}.`);
        }

        const extractedLines = allLines.slice(startIdx, endIdx);
        const content = extractedLines.join("\n");

        // Output path
        const safeId = nodeId.replace(/\./g, "_");
        const ext = extname(sourcePath);
        const name = basename(sourcePath, ext);
        const outputFilename = `${name}_${safeId}_lines_${startLine}-${endLine}${ext}`;
        const outputPath = join(outputDir, outputFilename);

        writeFileSync(outputPath, content, "utf-8");

        return {
            output_path: outputPath,
            resource_id: resourceId,
            modality: "text",
            address: buildAddress(resourceId, location),
            node: {
                id: nodeId,
                title: nodeId,
                type: "section",
                location: location
            }
        };
    }
}
