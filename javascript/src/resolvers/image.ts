import { join } from "node:path";
import { Resolver } from "./base.js";
import type { ResolvedEvidence } from "../models.js";

export class ImageResolver implements Resolver {
    async resolve(
        resourceId: string,
        nodeId: string,
        sourcePath: string,
        location: any,
        outputDir: string,
        options?: { virtual?: boolean }
    ): Promise<ResolvedEvidence> {
        // Virtual Resolution: Return BBox metadata without Sharp
        if (options?.virtual) {
            return {
                modality: "image",
                address: `img://${resourceId}#bbox=${location.bbox.join(",")}`,
                node: { id: nodeId, location: location } as any,
                resource_id: resourceId
            };
        }

        let sharp;
        try {
            const mod = await import("sharp");
            sharp = mod.default;
        } catch (e) {
            throw new Error(
                "The 'sharp' package is required for image resolution. " +
                "Please install it with: npm install sharp"
            );
        }

        if (!location.bbox || location.bbox.length !== 4) {
            throw new Error(`Node ${nodeId} missing valid bbox.`);
        }

        const [x1, y1, x2, y2] = location.bbox;

        // Load original to get dimensions
        const image = sharp(sourcePath);
        const metadata = await image.metadata();

        if (!metadata.width || !metadata.height) {
            throw new Error("Could not read image dimensions.");
        }

        const width = metadata.width;
        const height = metadata.height;

        // Convert normalized bbox (0-1) to pixel coordinates
        const left = Math.floor(x1 * width);
        const top = Math.floor(y1 * height);
        const cropWidth = Math.floor((x2 - x1) * width);
        const cropHeight = Math.floor((y2 - y1) * height);

        const filename = `${resourceId}_crop_${left}_${top}.png`;
        const outputPath = join(outputDir, filename);

        if (require("node:fs").existsSync(outputPath)) {
            return {
                output_path: outputPath,
                modality: "image",
                address: `image://${resourceId}#rect=${x1},${y1},${x2},${y2}`,
                node: { id: nodeId, location: location } as any,
                resource_id: resourceId
            };
        }

        await image
            .extract({ left, top, width: cropWidth, height: cropHeight })
            .toFile(outputPath);

        return {
            output_path: outputPath,
            modality: "image",
            address: `image://${resourceId}#rect=${x1},${y1},${x2},${y2}`,
            node: { id: nodeId, location: location } as any,
            resource_id: resourceId
        };
    }
}
