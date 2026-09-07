
from src.storage import get_articles_for_digest, mark_articles_as_sent
from src.email_sender import send_email


def build_digest_html(articles):
    """
    Build an HTML email containing the latest summarized tech articles.
    """

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Daily Tech Digest</title>
    </head>

    <body
        style="
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: auto;
            padding: 20px;
            line-height: 1.6;
        "
    >
        <h1>📰 Daily Tech Digest</h1>

        <p>
            Here are the latest summarized tech articles:
        </p>
    """

    for article in articles:
        title = article["title"]
        source = article["source"]
        url = article["url"]
        short_summary = article["short_summary"]
        detailed_summary = article["detailed_summary"]

        html += f"""
        <hr>

        <h2>
            <a
                href="{url}"
                style="
                    text-decoration: none;
                    color: #1a73e8;
                "
            >
                {title}
            </a>
        </h2>

        <p>
            <strong>Source:</strong> {source}
        </p>

        <p>
            {short_summary}
        </p>
        """

        if detailed_summary:
            html += f"""
            <h3>📌 Detailed Summary</h3>

            <p>
                {detailed_summary}
            </p>
            """

    html += """
    </body>
    </html>
    """

    return html


if __name__ == "__main__":
    # Get articles that are ready for the digest
    articles = get_articles_for_digest()

    print(f"Articles found: {len(articles)}")

    # Build the HTML email
    html = build_digest_html(articles)

    # Save a local preview
    with open(
        "digest_preview.html",
        "w",
        encoding="utf-8",
    ) as file:
        file.write(html)

    print("Digest HTML generated successfully.")
    print("Saved as: digest_preview.html")

    # Send the actual email only if articles are available
    if articles:
        article_ids = [article["id"] for article in articles]

        success = send_email(
            "📰 Daily Tech Digest",
            html,
        )

        # Mark articles as sent only after successful email delivery
        if success:
            mark_articles_as_sent(article_ids)
            print(f"Marked {len(article_ids)} article(s) as sent.")
        else:
            print(
                "Email was not sent. "
                "Articles were NOT marked as sent."
            )

    else:
        print("No articles available for the digest.")

