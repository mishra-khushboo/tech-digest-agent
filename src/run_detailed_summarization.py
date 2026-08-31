from storage import get_articles_needing_detailed_summary, update_detailed_summary
from summarizer import summarize_detailed


def main():
    articles = get_articles_needing_detailed_summary()

    print(f"Articles needing detailed summaries: {len(articles)}")

    summarized = 0
    failed = 0

    for article in articles:
        print(f"\n=== {article['title']} ===")
        print(f"Source: {article['source']}")

        summary = summarize_detailed(article["full_text"])

        if summary:
            update_detailed_summary(article["id"], summary)

            print("Detailed Summary:")
            print(summary)

            summarized += 1
        else:
            print("[WARN] No detailed summary generated")
            failed += 1

    print("\n=== Detailed Summarization Result ===")
    print(f"Summarized: {summarized}")
    print(f"Failed:     {failed}")


if __name__ == "__main__":
    main()