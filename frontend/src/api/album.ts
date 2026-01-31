import type { Album } from "../types/album";
import { apiGet, apiPost } from "./client";

export function getAlbums(): Promise<Album[]> {
  return apiGet<Album[]>("/api/albums");
}

export type SyncResult = { fetched: number; upserted: number };

export function syncAlbums(): Promise<SyncResult> {
  return apiPost<SyncResult>("/api/sync");
}
