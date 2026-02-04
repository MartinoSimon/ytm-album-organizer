import sqlite3
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]  # backend/
DB_PATH = BACKEND_DIR / "data" / "app.db"

TO_DELETE = ["test_ok_computer", "test_kid_a"]


def main() -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"No existe la DB en: {DB_PATH}")

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row

        # Preview
        q_marks = ",".join(["?"] * len(TO_DELETE))
        preview = conn.execute(
            f"SELECT playlist_id, title, artists_json, year FROM albums WHERE playlist_id IN ({q_marks})",
            TO_DELETE,
        ).fetchall()

        if not preview:
            print("No se encontró ningún registro para borrar.")
            return

        print("Encontrados para borrar:")
        for r in preview:
            print(dict(r))

        deleted = conn.execute(
            f"DELETE FROM albums WHERE playlist_id IN ({q_marks})",
            TO_DELETE,
        ).rowcount

        conn.commit()
        print(f"Borrados: {deleted}")


if __name__ == "__main__":
    main()
