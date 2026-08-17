import feedparser

FEEDS = {
    "Hacker News": "https://news.ycombinator.com/rss",
    "TechCrunch": "https://techcrunch.com/feed/",
    "arXiv CS": "http://export.arxiv.org/rss/cs",
}

MAX_ARTICLES_PER_SOURCE = 5


def fetch_feed(name, url, limit=MAX_ARTICLES_PER_SOURCE):
    print(f"\n--- {name} ---")
    parsed = feedparser.parse(url)

    if parsed.bozo:
        print(f"  WARNING: Feed may be malformed. Error: {parsed.bozo_exception}")

    print(f"  Found {len(parsed.entries)} entries total, keeping top {limit}")

    articles = []
    for entry in parsed.entries[:limit]:
        article = {
            "title": getattr(entry, "title", "No title"),
            "link": getattr(entry, "link", "No link"),
            "published": getattr(entry, "published", "No date"),
            "source": name,
        }
        articles.append(article)
        print(f"  - {article['title']}")
        print(f"    Link: {article['link']}")
        print(f"    Published: {article['published']}")

    return articles


def fetch_all_feeds():
    all_articles = []
    for name, url in FEEDS.items():
        articles = fetch_feed(name, url)
        all_articles.extend(articles)
    return all_articles


if __name__ == "__main__":
    all_articles = fetch_all_feeds()
    print(f"\nTotal articles collected: {len(all_articles)}")