from db import init_db
from fetch import fetch_all_feeds
from db import save_articles
from fetch_full_text import fetch_all_full_texts
from summarize import summarize_pending_detailed
from send_email import send_pending_digest


def run_pipeline():
    print("=== Step 1: Initializing database ===")
    try:
        init_db()
    except Exception as e:
        print(f"Failed to initialize database: {e}")
        return

    print("\n=== Step 2: Fetching RSS feeds ===")
    try:
        articles = fetch_all_feeds()
        save_articles(articles)
    except Exception as e:
        print(f"Failed to fetch/save articles: {e}")

    print("\n=== Step 3: Extracting full article text ===")
    try:
        fetch_all_full_texts()
    except Exception as e:
        print(f"Failed to extract full text: {e}")

    print("\n=== Step 4: Generating summaries ===")
    try:
        summarize_pending_detailed()
    except Exception as e:
        print(f"Failed to generate summaries: {e}")

    print("\n=== Step 5: Sending digest email ===")
    try:
        send_pending_digest()
    except Exception as e:
        print(f"Failed to send digest email: {e}")

    print("\n=== Pipeline run complete ===")


if __name__ == "__main__":
    run_pipeline()