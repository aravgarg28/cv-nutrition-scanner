// Public entry point for the generated SnapNutrition API client.
//
// `schema.ts` is generated from the API's OpenAPI document (see
// scripts/generate_openapi.py + `pnpm --filter @snap/api-client generate`) and is
// drift-checked in CI. Do not edit it by hand.

import createClient, { type ClientOptions } from "openapi-fetch";

import type { paths } from "./schema";

export type { components, paths } from "./schema";

/**
 * Create a typed API client bound to a base URL.
 *
 * @example
 *   const api = createApiClient({ baseUrl: "http://localhost:8000" });
 *   const { data } = await api.GET("/healthz");
 */
export function createApiClient(options: ClientOptions) {
  return createClient<paths>(options);
}

export type ApiClient = ReturnType<typeof createApiClient>;
