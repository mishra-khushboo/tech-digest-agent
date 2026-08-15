import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "digest.db"


def get_connection():
    """Open a connection to the SQLite database file (creates the file if it doesn't exist)."""
    return sqlite3.connect(DB_PATH)


def init_db():
    """Create the articles table if it doesn't already exist. Safe to call every run."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            source TEXT,
            published TEXT,
            full_text TEXT DEFAULT '',
            short_summary TEXT DEFAULT '',
            detailed_summary TEXT DEFAULT '',
            is_detailed INTEGER DEFAULT 0,
            sent_at TEXT DEFAULT NULL,
            fetched_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def insert_article(article):
    """
    Insert one article dict (with keys: title, url, source, published).
    If the URL already exists, this silently does nothing (dedupe via UNIQUE constraint).
    Returns True if a new row was inserted, False if it was a duplicate.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO articles (title, url, source, published)
            VALUES (?, ?, ?, ?)
        """, (article["title"], article["link"], article["source"], article["published"]))
        conn.commit()
        inserted = True
    except sqlite3.IntegrityError:
        # This fires when the UNIQUE constraint on url is violated — i.e. we've seen this article before
        inserted = False
    finally:
        conn.close()
    return inserted


def get_unsent_articles():
    """Return all articles that haven't been emailed yet (sent_at IS NULL), as a list of dicts."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row  # lets us access columns by name instead of index
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM articles WHERE sent_at IS NULL")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


if __name__ == "__main__":
    from ingest import FEEDS, fetch_latest

    init_db()

    total_inserted = 0
    total_duplicates = 0

    for feed_name, feed_url in FEEDS:
        print(f"\n=== {feed_name} ===")

        articles = fetch_latest(feed_name, feed_url)

        for article in articles:
            if insert_article(article):
                total_inserted += 1
                print(f"[NEW] {article['title']}")
            else:
                total_duplicates += 1
                print(f"[DUPLICATE] {article['title']}")

    print("\n=== Storage Result ===")
    print(f"New articles: {total_inserted}")
    print(f"Duplicates:   {total_duplicates}")