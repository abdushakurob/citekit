import type { ResourceMap } from "../models.js";

export interface MapperProvider {
    generateMap(
        resourcePath: string,
        resourceType: string,
        resourceId?: string
    ): Promise<ResourceMap>;
}
