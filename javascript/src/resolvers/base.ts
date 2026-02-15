import type { ResolvedEvidence } from "../models.js";

export interface Resolver {
    resolve(
        resourceId: string,
        nodeId: string,
        sourcePath: string,
        location: any,
        outputDir: string,
        options?: { virtual?: boolean }
    ): Promise<ResolvedEvidence>;
}
