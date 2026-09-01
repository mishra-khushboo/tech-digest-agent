from datetime import datetime
import html

from storage import get_articles_for_digest


def format_summary(summary):
    """
    Convert simple Markdown-style formatting from the LLM
    into readable HTML.
    """
    lines = summary.splitlines()
    output = []
    in_list = False

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Headings like **Main Topic:**
        if line.startswith("**") and line.endswith("**"):
            if in_list:
                output.append("</ul>")
                in_list = False

            heading = line.strip("*")
            output.append(f"<h4>{html.escape(heading)}</h4>")

        # Bullet points
        elif line.startswith("* "):
            if not in_list:
                output.append("<ul>")
                in_list = True

            item = line[2:]
            output.append(f"<li>{html.escape(item)}</li>")

        else:
            if in_list:
                output.append("</ul>")
                in_list = False

            output.append(f"<p>{html.escape(line)}</p>")

    if in_list:
        output.append("</ul>")

    return "\n".join(output)


def build_digest_html(articles):
    """
    Build a clean HTML email containing the latest summarized
    tech articles.
    """

    today = datetime.now().strftime("%d %B %Y")

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <title>Daily Tech Digest</title>
    </head>

    <body style="
        margin: 0;
        padding: 0;
        background-color: #f4f4f4;
        font-family: Arial, sans-serif;
    ">

        <div style="
            max-width: 800px;
            margin: 30px auto;
            background: white;
            padding: 30px;
        ">

            <h1 style="margin-bottom: 5px;">
                📰 Daily Tech Digest
            </h1>

            <p style="color: #666;">
                {today}
            </p>

            <p>
                Here are today's latest technology articles.
            </p>
    """

    for article in articles:
        title = html.escape(article["title"])
        source = html.escape(article["source"] or "Unknown")
        url = html.escape(article["url"], quote=True)

        short_summary = html.escape(
            article["short_summary"] or ""
        )

        detailed_summary = article["detailed_summary"]

        html_content += f"""
        <hr style="margin: 30px 0;">

        <article>

            <p style="
                color: #666;
                font-size: 14px;
                margin-bottom: 8px;
            ">
                {source}
            </p>

            <h2 style="margin-top: 0;">
                <a href="{url}"
                   style="
                       color: #222;
                       text-decoration: none;
                   ">
                    {title}
                </a>
            </h2>

            <p style="
                font-size: 16px;
                line-height: 1.6;
            ">
                {short_summary}
            </p>
        """

        if detailed_summary:
            html_content += f"""
            <div style="
                margin-top: 20px;
                padding: 20px;
                background: #f7f7f7;
                border-left: 4px solid #555;
            ">

                <h3>
                    Detailed Summary
                </h3>

                <div style="
                    line-height: 1.6;
                ">
                    {format_summary(detailed_summary)}
                </div>

            </div>
            """

        html_content += """
        </article>
        """

    html_content += """
        </div>

    </body>
    </html>
    """

    return html_content


if __name__ == "__main__":
    articles = get_articles_for_digest()

    print(f"Articles found: {len(articles)}")

    html_content = build_digest_html(articles)

    with open("digest_preview.html", "w", encoding="utf-8") as file:
        file.write(html_content)

    print("Digest HTML generated successfully.")
    print("Saved as: digest_preview.html")