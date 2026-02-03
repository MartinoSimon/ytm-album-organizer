import { useEffect, useState } from "react";
import type { Album } from "../types/album";
import { getAlbums, syncAlbums } from "../api/album";

type LoadStatus = "idle" | "loading" | "success" | "error";
type SortKey = "title" | "year" | "artist" ;
type SortDir = "asc" | "desc";



export default function Library() {

  const [status, setStatus] = useState<LoadStatus>("idle");
  const [error, setError] = useState<string | null>(null);
  const [albums, setAlbums] = useState<Album[]>([]);
  const [syncing, setSyncing] = useState(false);
  const [syncMsg, setSyncMsg] = useState<string | null>(null);
  const [query, setQuery] = useState<string>("");
  const [sortKey, setSortKey] = useState<SortKey>("title");
  const [sortDir, setSortDir] = useState<SortDir>("asc");


  async function handleSync() {
    setSyncing(true);
    setError(null);
    try {
      const r = await syncAlbums();     // POST /api/sync
      setSyncMsg(`Synced: ${r.fetched} (upserted: ${r.upserted})`);
      await loadAlbums();     // refresca GET /api/albums
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      setError(message);
      setStatus("error");
    } finally {
      setSyncing(false);
    }
  }

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

  function filterAlbums(albums: Album[]): Album[] {
    const q = query.trim().toLowerCase(); 

    if (q === "") return albums;

    return albums.filter((a) => {
      const searchable =
        `${a.title} ${a.artists.join(" ")} ${a.year ?? ""}`.toLowerCase();

      return searchable.includes(q);
    });
  }

  function sortAlbums(albums: Album[]): Album[] {
    const unsortedAlbums = [...albums];
    const dir = (sortDir === "asc" ? 1 : -1)
    if (sortKey == "title") {
      unsortedAlbums.sort((a,b) => a.title.toLowerCase().localeCompare(b.title.toLowerCase()) * dir);
    } else if (sortKey == "artist") {
      unsortedAlbums.sort((a,b) => a.artists.join(" ").toLowerCase().localeCompare(b.artists.join(" ").toLowerCase()) * dir)
    } else if (sortKey == "year") {
      unsortedAlbums.sort((a,b) => {
        if (a.year == null){
          if (b.year == null) {
            return 0
          } else {
            return 1
          } } else if (b.year == null) {
            return -1
          } else {
            return (a.year - b.year) * dir;
          }
        }
      )
    }
    return unsortedAlbums
  }

function renderAlbums(albums: Album[]) {
  const filtered = filterAlbums(albums);
  const sorted = sortAlbums(filtered);

  return (
    <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
      {sorted.map((a) => {
        const ytmURL = "https://music.youtube.com/playlist?list=" + a.playlistId;
        return (<li>
  <a
    className="albumItem"
    href={ytmURL}
    target="_blank"
    rel="noopener noreferrer"
  >
    <img
              src={a.coverUrl ?? ""}
              loading="lazy"
              alt={`${a.title} cover`}
              style={{
                width: 48,
                height: 48,
                borderRadius: 8,
                marginRight: 12,
                objectFit: "cover",
                verticalAlign: "middle",
              }}
            />
    <strong>{a.title}</strong> — {a.artists.join(", ")}
    {a.year !== null ? ` (${a.year})` : ""}
    
  </a>
</li>)

})}
    </ul>
  );
}



  return (
    <div>
      <h1>Library</h1>
      <button onClick={loadAlbums} disabled={status === "loading"}>
        {status === "loading" ? "Refreshing..." : "Refresh"}
      </button>

      <label htmlFor="query">Query by name of Artists, Album, Year</label>
      <input type="text" id="query" name="query" value={query} 
      onChange={(e) => setQuery(e.target.value)} maxLength={60} />

      <label htmlFor="sortKey">Sort by</label>
      <select id="sortKey" value={sortKey} onChange={(e) => setSortKey(e.target.value as SortKey)}>
        <option value="artist">Artists</option>
        <option value="title">Album</option>
        <option value="year">Year</option>
      </select>

      <label htmlFor="sortDir">Order</label>
      <select id="sortDir" value={sortDir} onChange={(e) => setSortDir(e.target.value as SortDir)}>
          <option value="asc">Ascending</option>
          <option value="desc">Descending</option>
      </select>

      <div style={{ marginTop: 12 }}>
        {status === "loading" && <p>Loading...</p>}

        {status === "error" && <p>Error: {error}</p>}

        {status === "success" && albums.length === 0 && <p>0 albums</p>}

        {status === "success" && albums.length > 0 && renderAlbums(albums)}
      </div>

    <button onClick={loadAlbums} disabled={status === "loading" || syncing}>
      {status === "loading" ? "Refreshing..." : "Refresh"}</button>

    <button
      onClick={handleSync}
      disabled={syncing || status === "loading"}
      style={{ marginLeft: 8 }}>
      {syncing ? "Syncing..." : "Sync"}
    </button>
        {syncMsg && <p>{syncMsg}</p>}
    </div>
  );
}
