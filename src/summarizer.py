import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:1b"


def summarize_short(article_text, max_chars=6000):
    """
    Send article text to the local Ollama model and return a short,
    2-3 line summary. Returns an empty string if the request fails.
    """
    # Truncate very long articles — keeps prompts fast and avoids
    # overwhelming a small local model with more context than it needs
    text = article_text[:max_chars]

    prompt = (
    "Summarize the following tech news article in exactly 2 or 3 concise sentences. "
    "Write only the summary. Do not include headings, bullet points, labels, "
    "introductions, or phrases like 'Here is a summary'. "
    "Focus only on the most important facts.\n\n"
    f"Article:\n{text}\n\nSummary:"
    )

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
            },
            timeout=180,
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[WARN] Ollama request failed: {e}")
        return ""

    data = response.json()
    return data.get("response", "").strip()


if __name__ == "__main__":
    from storage import get_articles_needing_summary, update_short_summary

    articles = get_articles_needing_summary()
    print(f"Found {len(articles)} article(s) needing a summary.\n")

    for article in articles:
        print(f"Summarizing: {article['title']}")
        summary = summarize_short(article["full_text"])

        if summary:
            update_short_summary(article["id"], summary)
            print(f"  -> {summary}\n")
        else:
            print("  -> [WARN] no summary generated, skipping\n")

    print("Done.")