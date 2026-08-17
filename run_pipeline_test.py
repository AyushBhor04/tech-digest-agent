from fetch import fetch_all_feeds
from db import init_db, save_articles, get_all_articles

def main():
    print("Initializing database...")
    init_db()

    print("\nFetching articles...")
    articles = fetch_all_feeds()
    print(f"\nFetched {len(articles)} articles total.")

    print("\nSaving to database...")
    save_articles(articles)

    print("\nCurrent articles in database:")
    for row in get_all_articles():
        print(f"  id={row[0]} | source={row[2]} | sent={row[4]} | title={row[1]}")

if __name__ == "__main__":
    main()