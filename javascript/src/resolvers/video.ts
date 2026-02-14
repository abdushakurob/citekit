import ffmpeg from "fluent-ffmpeg";
import { join } from "node:path";
import { Resolver } from "./base.js";
import type { ResolvedEvidence } from "../models.js";

export class VideoResolver implements Resolver {
    async resolve(
        resourceId: string,
        nodeId: string,
        sourcePath: string,
        location: any,
        outputDir: string
    ): Promise<ResolvedEvidence> {
        if (location.start === undefined || location.end === undefined) {
            throw new Error(`Node ${nodeId} missing start/end times.`);
        }

        const start = location.start;
        const duration = location.end - location.start;

        const filename = `${resourceId}_clip_${start}_${location.end}.mp4`;
        const outputPath = join(outputDir, filename);

        return new Promise((resolve, reject) => {
            ffmpeg(sourcePath)
                .setStartTime(start)
                .setDuration(duration)
                .output(outputPath)
                .on("end", () => {
                    resolve({
                        output_path: outputPath,
                        modality: "video",
                        address: `video://${resourceId}#t=${start},${location.end}`,
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
