import { existsSync } from "node:fs";
import { join } from "node:path";
import { Resolver } from "./base.js";
import type { ResolvedEvidence } from "../models.js";
import { buildAddress } from "../address.js";

export class AudioResolver implements Resolver {
    async resolve(
        resourceId: string,
        nodeId: string,
        sourcePath: string,
        location: any,
        outputDir: string,
        options?: { virtual?: boolean }
    ): Promise<ResolvedEvidence> {
        if (options?.virtual) {
            return {
                modality: "audio",
                address: buildAddress(resourceId, location),
                node: { id: nodeId, location: location } as any,
                resource_id: resourceId
            };
        }

        let ffmpeg;
        try {
            const mod = await import("fluent-ffmpeg");
            ffmpeg = mod.default;
        } catch (e) {
            throw new Error(
                "The 'fluent-ffmpeg' package is required for audio resolution. " +
                "Please install it with: npm install fluent-ffmpeg"
            );
        }

        if (!existsSync(sourcePath)) {
            throw new Error(`Source file not found: ${sourcePath}`);
        }

        if (location.start === undefined || location.end === undefined) {
            throw new Error(`Node ${nodeId} missing start/end times.`);
        }

        const start = location.start;
        const duration = location.end - location.start;

        const filename = `${resourceId}_audio_${start}_${location.end}.mp3`;
        const outputPath = join(outputDir, filename);

        if (existsSync(outputPath)) {
            return {
                output_path: outputPath,
                modality: "audio",
                address: buildAddress(resourceId, location),
                node: { id: nodeId, location: location } as any,
                resource_id: resourceId
            };
        }

        return new Promise((resolve, reject) => {
            ffmpeg(sourcePath)
                .setStartTime(start)
                .setDuration(duration)
                .output(outputPath)
                .on("end", () => {
                    resolve({
                        output_path: outputPath,
                        modality: "audio",
                        address: buildAddress(resourceId, location),
                        node: { id: nodeId, location: location } as any,
                        resource_id: resourceId
                    });
                })
                .on("error", (err) => {
                    reject(new Error(`ffmpeg failed: ${err.message}`));
                })
                .run();
        });
    }
}
