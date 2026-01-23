import type { Album } from "../types/album";
import { apiGet } from "./client";

export function getAlbums(): Promise<Album[]> {
  return apiGet<Album[]>("/api/albums");
}
