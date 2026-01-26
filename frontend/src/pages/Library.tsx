import { useEffect, useState } from "react";
import type { Album } from "../types/album";
import { getAlbums } from "../api/album";

type LoadStatus = "idle" | "loading" | "success" | "error";


export default function Library() {

  const [status, setStatus] = useState<LoadStatus>("idle");
  const [error, setError] = useState<string | null>(null);
  const [albums, setAlbums] = useState<Album[]>([]);

 async function loadAlbums() {
    setStatus("loading");
    setError(null);

    try {
      const data = await getAlbums();
      setAlbums(data);
      setStatus("success");
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      setError(message);
      setStatus("error");
    }
  }

  useEffect(() => {
    const t = setTimeout(() => void loadAlbums(), 0);
    return () => clearTimeout(t);
  }, []);
  // useEffect(() => {loadAlbums()},[])

  return (
    <div>
      <h1>Library</h1>
      <button onClick={loadAlbums} disabled={status === "loading"}>
        {status === "loading" ? "Refreshing..." : "Refresh"}
      </button>
      <div style={{ marginTop: 12 }}>
        {status === "loading" && <p>Loading...</p>}

        {status === "error" && <p>Error: {error}</p>}

        {status === "success" && albums.length === 0 && <p>0 albums</p>}

        {status === "success" && albums.length > 0 && (
          <ul>
            {albums.map((a) => (
              <li key={a.playlistId}>
                <strong>{a.title}</strong> — {a.artists.join(", ")}
                {a.year !== null ? ` (${a.year})` : ""}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
