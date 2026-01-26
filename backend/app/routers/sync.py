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
INSERT INTO albums (playlist_id, title, artists_json, year, genre)
VALUES (?, ?, ?, ?, ?)
ON CONFLICT(playlist_id) DO UPDATE SET
  title        = excluded.title,
  artists_json = excluded.artists_json,
  year         = excluded.year,
  genre        = COALESCE(excluded.genre, albums.genre);
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
            pid = a.get("playlistId") or a.get("browseId") or ""
            title = a.get("title") or ""
            artists = [x.get("name") for x in a.get("artists", []) if x.get("name")]
            year = a.get("year")
            # year puede venir como string; lo normalizamos a int si se puede
            try:
                year_int = int(year) if year is not None else None
            except (TypeError, ValueError):
                year_int = None

            rows.append((pid, title, json.dumps(artists, ensure_ascii=False), year_int, None))

        upserted = upsert_albums(rows)
        return {"fetched": len(albums), "upserted": upserted}

    return await to_thread.run_sync(_work)
