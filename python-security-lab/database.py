import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("lab.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)

    existing = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if existing == 0:
        # Demo-only credentials. Never store plaintext passwords in production.
        conn.executemany(
            "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
            [
                ("alice", "alice123", "alice@example.test"),
                ("bob", "bob123", "bob@example.test"),
            ],
        )
    conn.commit()
    conn.close()
