CREATE TABLE IF NOT EXISTS albums(
    playlist_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    artists_json TEXT NOT NULL,
    year INTEGER,
    genre TEXT,
    added_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_albums_added_at ON albums(added_at);
CREATE INDEX IF NOT EXISTS idx_albums_year ON albums(year);
