"""Initialize the SQLite database."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "opsagent.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def init():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")


if __name__ == "__main__":
    init()
