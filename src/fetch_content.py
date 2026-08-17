import requests
import trafilatura


def fetch_full_text(url, timeout=15):
    """
    Download an article webpage and extract its main readable text.

    Returns:
        str: Clean article text, or an empty string if fetching
        or extraction fails.
    """

    try:
        response = requests.get(
            url,
            timeout=timeout,
            headers={
                "User-Agent": "tech-digest-agent/0.1"
            }
        )

        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        print(f"[WARN] Could not fetch {url}: {e}")
        return ""

    text = trafilatura.extract(response.content)

    if not text:
        print(f"[WARN] Could not extract article text from {url}")
        return ""

    return text


if __name__ == "__main__":
    test_urls = [
        "https://techcrunch.com/2026/08/15/every-fusion-startup-that-has-raised-over-100m/",
        "https://arxiv.org/abs/2608.12325",
        "https://news.ycombinator.com/rss",  # not an article page — should fail gracefully
    ]

    for url in test_urls:
        print(f"\n=== {url} ===")
        text = fetch_full_text(url)
        if text:
            print(f"Extracted {len(text)} characters")
            print(text[:300] + "...")
        else:
            print("(no text extracted)")