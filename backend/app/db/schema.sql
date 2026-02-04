CREATE TABLE IF NOT EXISTS albums(
    playlist_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    artists_json TEXT NOT NULL,
    year INTEGER,
    genre TEXT,
    browse_id TEXT,
    cover_url TEXT,
    track_count INTEGER,
    duration_text TEXT,
    description TEXT
);

CREATE INDEX IF NOT EXISTS idx_albums_added_at ON albums(added_at);
CREATE INDEX IF NOT EXISTS idx_albums_year ON albums(year);
