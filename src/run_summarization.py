from storage import get_articles_needing_summary, update_short_summary
from summarizer import summarize_short


def main():
    articles = get_articles_needing_summary()

    print(f"Articles needing summaries: {len(articles)}")

    summarized = 0
    failed = 0

    for article in articles:
        print(f"\n=== {article['title']} ===")

        summary = summarize_short(article["full_text"])

        if summary:
            update_short_summary(article["id"], summary)

            print("Summary:")
            print(summary)

            summarized += 1
        else:
            print("[WARN] No summary generated")
            failed += 1

    print("\n=== Summarization Result ===")
    print(f"Summarized: {summarized}")
    print(f"Failed:     {failed}")


if __name__ == "__main__":
    main()
