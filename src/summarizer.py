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
        "Summarize the following tech news article in 2-3 concise sentences. "
        "Focus on the key facts only. Do not add commentary or opinions.\n\n"
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
    sample_text = """
    OpenAI announced a new version of its flagship model today, claiming
    significant improvements in reasoning and coding tasks. The company said
    the model was trained on a larger dataset and uses a new architecture
    that reduces hallucination rates by 40% compared to its predecessor.
    Early access will be rolled out to enterprise customers first, with
    general availability expected within the next two months. Pricing
    details have not yet been announced.
    """

    print("Sending sample article to Ollama...")
    summary = summarize_short(sample_text)
    print("\n=== Summary ===")
    print(summary if summary else "(no summary generated)")