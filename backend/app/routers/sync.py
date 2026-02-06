import json
import sqlite3
from pathlib import Path

from anyio import to_thread
from fastapi import APIRouter
from ytmusicapi import YTMusic

router = APIRouter(prefix="/api", tags=["sync"])

BACKEND_DIR = Path(__file__).resolve().parents[2]   # backend/
DATA_DIR = BACKEND_DIR / "data"

DB_PATH = DATA_DIR / "app.db"
BROWSER_PATH = DATA_DIR / "browser.json"

UPSERT_SQL = """
INSERT INTO albums (playlist_id, title, artists_json, year, genre, browse_id, cover_url)
VALUES (?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(playlist_id) DO UPDATE SET
  title        = excluded.title,
  artists_json = excluded.artists_json,
  year         = excluded.year,
  genre        = COALESCE(excluded.genre, albums.genre),
  browse_id    = excluded.browse_id,
  cover_url    = COALESCE(excluded.cover_url, albums.cover_url);
"""

def upsert_albums(rows):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.executemany(UPSERT_SQL, rows)
        conn.commit()
        return cur.rowcount

@router.post("/sync")
async def sync_albums():
    def _work():
        if not BROWSER_PATH.exists():
            raise RuntimeError(f"Falta {BROWSER_PATH}")

        ytm = YTMusic(str(BROWSER_PATH))
        albums = ytm.get_library_albums(limit=5000)

        rows = []
        for a in albums:
            pid = a.get("playlistId") or a.get("browseId")
            if not pid:
                continue
            title = a.get("title") or ""
            artists = [x.get("name") for x in a.get("artists", []) if x.get("name")]
            year = a.get("year")
            try:
                year_int = int(year) if year is not None else None
            except (TypeError, ValueError):
                year_int = None
            browse_id = a.get("browseId")
            thumbs = a.get("thumbnails", [])
            if thumbs == [] and browse_id:
                details = ytm.get_album(browse_id)
                thumbs2 = details.get("thumbnails",[])
                if thumbs2 == []:
                    cover_url = None
                else:
                    cover_url = max(thumbs2, key=lambda t: t.get("width",0)).get("url")
            else:
                cover_url = max(thumbs, key=lambda t: t.get("width",0)).get("url")

            rows.append((pid, title, json.dumps(artists, ensure_ascii=False), year_int, None, browse_id, cover_url))

        upserted = upsert_albums(rows)
        return {"fetched": len(albums), "upserted": upserted}

    return await to_thread.run_sync(_work)
