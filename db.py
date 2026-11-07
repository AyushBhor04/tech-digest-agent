
import sqlite3
from datetime import datetime

DB_NAME = "articles.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            link TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            source TEXT NOT NULL,
            published TEXT,
            full_text TEXT,
            quick_summary TEXT,
            detailed_summary TEXT,
            sent INTEGER DEFAULT 0,
            fetched_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_articles(articles):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    inserted_count = 0
    skipped_count = 0

    for article in articles:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO articles (link, title, source, published, fetched_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                article["link"],
                article["title"],
                article["source"],
                article["published"],
                datetime.now().isoformat()
            ))

            if cursor.rowcount == 1:
                inserted_count += 1
            else:
                skipped_count += 1

        except sqlite3.Error as e:
            print(f"  Error inserting article '{article['title']}': {e}")

    conn.commit()
    conn.close()

    print(f"Inserted {inserted_count} new articles, skipped {skipped_count} duplicates.")


def get_all_articles():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, source, link, sent FROM articles")

    rows = cursor.fetchall()
    conn.close()

    return rows


def get_articles_without_summary():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, link FROM articles
        WHERE quick_summary IS NULL OR quick_summary = ''
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows


def update_summary(article_id, summary):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE articles SET quick_summary = ? WHERE id = ?
    """, (summary, article_id))

    conn.commit()
    conn.close()


def get_articles_without_full_text():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, link FROM articles WHERE (full_text IS NULL OR full_text = '') AND sent = 0")

    rows = cursor.fetchall()
    conn.close()

    return rows


def update_full_text(article_id, text):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE articles SET full_text = ? WHERE id = ?
    """, (text, article_id))

    conn.commit()
    conn.close()


def get_articles_without_detailed_summary():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, full_text FROM articles
        WHERE (detailed_summary IS NULL OR detailed_summary = '')
        AND full_text IS NOT NULL AND full_text != ''
        AND sent = 0
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows


def update_detailed_summary(article_id, summary):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE articles SET detailed_summary = ? WHERE id = ?
    """, (summary, article_id))

    conn.commit()
    conn.close()


def get_unsent_articles_full():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, source, link, quick_summary, detailed_summary
        FROM articles
        WHERE sent = 0
        ORDER BY source, id
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows


def mark_articles_as_sent(article_ids):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.executemany(
        "UPDATE articles SET sent = 1 WHERE id = ?",
        [(article_id,) for article_id in article_ids]
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized. Table 'articles' is ready.")
