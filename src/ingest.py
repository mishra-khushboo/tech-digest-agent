import feedparser

# Feeds we're pulling from — name is just for display/logging
FEEDS = [
    ("Hacker News", "https://news.ycombinator.com/rss"),
    ("TechCrunch", "https://techcrunch.com/feed/"),
    ("arXiv cs.AI", "https://export.arxiv.org/rss/cs.AI"),
]


def fetch_latest(feed_name, feed_url, limit=5):
    """
    Fetch a single RSS feed and return a list of dictionaries.
    """
    parsed = feedparser.parse(feed_url)

    if parsed.bozo:
        print(f"[WARN] Problem fetching {feed_name}: {parsed.bozo_exception}")
        return []

    articles = []

    for entry in parsed.entries[:limit]:
        articles.append({
            "title": entry.get("title", "No title"),
            "link": entry.get("link", ""),
            "published": entry.get("published", "Unknown date"),
            "source": feed_name,
        })

    return articles


if __name__ == "__main__":
    for name, url in FEEDS:
        print(f"\n=== {name} ===")

        items = fetch_latest(name, url)

        if not items:
            print("  (no items fetched)")

        for item in items:
            print(f"- {item['title']}")
            print(f"  {item['link']}")
            print(f"  Published: {item['published']}")