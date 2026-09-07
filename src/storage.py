import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "data" / "digest.db"


def get_connection():
    """Open a connection to the SQLite database file."""
    return sqlite3.connect(DB_PATH)


def init_db():
    """Create the articles table if it doesn't already exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
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
        """
    )

    conn.commit()
    conn.close()


def insert_article(article):
    """
    Insert one article into the database.

    Returns:
        New article ID if inserted.
        None if the article already exists.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO articles (
                title,
                url,
                source,
                published
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                article["title"],
                article["link"],
                article["source"],
                article["published"],
            ),
        )

        conn.commit()
        new_id = cursor.lastrowid

    except sqlite3.IntegrityError:
        new_id = None

    finally:
        conn.close()

    return new_id


def update_full_text(article_id, full_text):
    """Save extracted full article text."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE articles
        SET full_text = ?
        WHERE id = ?
        """,
        (full_text, article_id),
    )

    conn.commit()
    conn.close()


def update_short_summary(article_id, summary):
    """Save the short summary for an article."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE articles
        SET short_summary = ?
        WHERE id = ?
        """,
        (summary, article_id),
    )

    conn.commit()
    conn.close()


def update_detailed_summary(article_id, summary):
    """Save the detailed summary for an article."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE articles
        SET detailed_summary = ?
        WHERE id = ?
        """,
        (summary, article_id),
    )

    conn.commit()
    conn.close()


def get_articles_needing_summary():
    """Return articles that have full text but no short summary."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM articles
        WHERE full_text != ''
        AND short_summary = ''
        """
    )

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_articles_needing_detailed_summary(limit_per_source=2):
    """
    Return up to limit_per_source articles per source
    that have full text but no detailed summary.
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """
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
        """,
        (limit_per_source,),
    )

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_unsent_articles():
    """Return all articles that haven't been emailed yet."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM articles
        WHERE sent_at IS NULL
        """
    )

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_articles_for_digest():
    """Return unsent articles that have a short summary."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM articles
        WHERE sent_at IS NULL
        AND short_summary != ''
        ORDER BY published DESC
        """
    )

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def mark_articles_as_sent(article_ids):
    """
    Mark the given articles as successfully sent.

    Args:
        article_ids: List of article IDs.
    """
    if not article_ids:
        return

    conn = get_connection()
    cursor = conn.cursor()

    placeholders = ",".join("?" for _ in article_ids)

    cursor.execute(
        f"""
        UPDATE articles
        SET sent_at = CURRENT_TIMESTAMP
        WHERE id IN ({placeholders})
        """,
        article_ids,
    )

    conn.commit()
    conn.close()


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

                    print(
                        f"      -> fetched "
                        f"{len(full_text)} characters of full text"
                    )
                else:
                    print("      -> no full text extracted")

            else:
                total_duplicates += 1

                print(f"[DUPLICATE] {article['title']}")

    print("\n=== Storage Result ===")
    print(f"New articles: {total_inserted}")
    print(f"Duplicates:   {total_duplicates}")
