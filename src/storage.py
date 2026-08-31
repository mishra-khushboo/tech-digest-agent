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
    Returns the new row's id if inserted, or None if it was a duplicate.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO articles (title, url, source, published)
            VALUES (?, ?, ?, ?)
        """, (article["title"], article["link"], article["source"], article["published"]))
        conn.commit()
        new_id = cursor.lastrowid  # the auto-incremented id SQLite just assigned
    except sqlite3.IntegrityError:
        # This fires when the UNIQUE constraint on url is violated — i.e. we've seen this article before
        new_id = None
    finally:
        conn.close()
    return new_id


def update_full_text(article_id, full_text):
    """Save extracted full article text for a given article id."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE articles SET full_text = ? WHERE id = ?
    """, (full_text, article_id))
    conn.commit()
    conn.close()


def update_short_summary(article_id, summary):
    """Save the short summary for a given article."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE articles
        SET short_summary = ?
        WHERE id = ?
    """, (summary, article_id))

    conn.commit()
    conn.close()

def update_detailed_summary(article_id, summary):
    """Save the detailed summary for a given article."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE articles
        SET detailed_summary = ?
        WHERE id = ?
    """, (summary, article_id))

    conn.commit()
    conn.close()

def get_articles_needing_summary():
    """Return articles that have full text but no short summary."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM articles
        WHERE full_text != ''
        AND short_summary = ''
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]

def get_articles_needing_detailed_summary(limit_per_source=2):
    """
    Return up to `limit_per_source` articles per source that have full text
    but no detailed summary yet.
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM (
            SELECT *,
                   ROW_NUMBER() OVER (
                       PARTITION BY source
                       ORDER BY published DESC
                   ) AS row_num
            FROM articles
            WHERE full_text != ''
            AND detailed_summary = ''
        )
        WHERE row_num <= ?
        ORDER BY source, published DESC
    """, (limit_per_source,))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]

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
    from fetch_content import fetch_full_text

    init_db()

    total_inserted = 0
    total_duplicates = 0

    for feed_name, feed_url in FEEDS:
        print(f"\n=== {feed_name} ===")

        articles = fetch_latest(feed_name, feed_url)

        for article in articles:
            new_id = insert_article(article)
            if new_id is not None:
                total_inserted += 1
                print(f"[NEW] {article['title']}")

                full_text = fetch_full_text(article["link"])
                if full_text:
                    update_full_text(new_id, full_text)
                    print(f"      -> fetched {len(full_text)} characters of full text")
                else:
                    print(f"      -> no full text extracted")
            else:
                total_duplicates += 1
                print(f"[DUPLICATE] {article['title']}")

    print("\n=== Storage Result ===")
    print(f"New articles: {total_inserted}")
    print(f"Duplicates:   {total_duplicates}")