import json
from app.db.database import get_conn, init_db

SEED_ALBUMS = [
    {
        "playlist_id": "test_kid_a",
        "title": "Kid A",
        "artists": ["Radiohead"],
        "year": 2000,
        "genre": "Alternative",
    },
    {
        "playlist_id": "test_ok_computer",
        "title": "OK Computer",
        "artists": ["Radiohead"],
        "year": 1997,
        "genre": "Alternative",
    },
]

def main() -> None:
    init_db()

    with get_conn() as conn:
        for a in SEED_ALBUMS:
            conn.execute(
                """
                INSERT OR REPLACE INTO albums
                (playlist_id, title, artists_json, year, genre)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    a["playlist_id"],
                    a["title"],
                    json.dumps(a["artists"]),
                    a["year"],
                    a["genre"],
                ),
            )

    print(f"Seeded {len(SEED_ALBUMS)} albums.")

if __name__ == "__main__":
    main()
