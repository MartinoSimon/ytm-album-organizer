import json
from fastapi import APIRouter
from app.db.database import get_conn

router = APIRouter(prefix="/api", tags=["albums"])

@router.get("/albums")
def list_albums():
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT playlist_id, title, artists_json, year, browse_id, cover_url
            FROM albums
            ORDER BY added_at DESC
            """
        ).fetchall()

    albums = []
    for r in rows:
        albums.append({
            "playlistId": r["playlist_id"],
            "title": r["title"],
            "artists": json.loads(r["artists_json"]) if r["artists_json"] else [],
            "year": r["year"],
            "browseId": r["browse_id"],
            "coverUrl": r["cover_url"],
        })

    return albums
