
from datetime import date
from db import get_unsent_articles_full


def build_digest_html():
    articles = get_unsent_articles_full()

    # Keep only articles that actually have a detailed summary
    articles = [a for a in articles if a[5]]

    if not articles:
        return None, []  # Nothing new to send

    # Group articles by source
    grouped = {}

    for article_id, title, source, link, quick_summary, detailed_summary in articles:
        grouped.setdefault(source, []).append({
            "id": article_id,
            "title": title,
            "link": link,
            "summary": detailed_summary
        })

    today_str = date.today().strftime("%B %d, %Y")

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
        <div style="max-width: 700px; margin: auto; background-color: #ffffff; padding: 20px; border-radius: 8px;">
            <h1 style="color: #222; font-size: 22px;">Tech Digest — {today_str}</h1>
    """

    for source, source_articles in grouped.items():

        html += f'<h2 style="color: #444; font-size: 18px; border-bottom: 1px solid #ddd; padding-bottom: 5px;">{source}</h2>'

        for a in source_articles:
            html += f"""
            <div style="margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid #eee;">
                <a href="{a['link']}" style="font-size: 16px; font-weight: bold; color: #1a73e8; text-decoration: none;">
                    {a['title']}
                </a>
                <p style="font-size: 14px; color: #333; margin: 8px 0;">
                    {a['summary']}
                </p>
            </div>
            """

    html += """
        </div>
    </body>
    </html>
    """

    # Return both the HTML and the IDs of included articles
    article_ids = [a[0] for a in articles]

    return html, article_ids


if __name__ == "__main__":
    digest_html, article_ids = build_digest_html()

    if digest_html is None:
        print("No unsent articles — nothing to compose.")
    else:
        with open("preview_digest.html", "w", encoding="utf-8") as f:
            f.write(digest_html)

        print("Digest HTML generated and saved to preview_digest.html")
        print(
            f"Open it in your browser to preview: "
            f"{__file__.replace('compose_email.py', 'preview_digest.html')}"
        )
