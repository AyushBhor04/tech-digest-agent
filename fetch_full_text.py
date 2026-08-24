import requests
from bs4 import BeautifulSoup
from db import get_articles_without_full_text, update_full_text

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

MIN_PARAGRAPH_LENGTH = 40  # skip junk like "Subscribe now" or "Share this"


def extract_full_text(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"  Failed to fetch page: {e}")
        return ""

    soup = BeautifulSoup(response.text, "html.parser")

    # Special case: arXiv abstract pages store the abstract in a <blockquote>,
    # not in generic <p> tags, so the general heuristic below would miss it.
    if "arxiv.org" in url:
        abstract_block = soup.find("blockquote", class_="abstract")
        if abstract_block:
            text = abstract_block.get_text().strip()
            # arXiv prefixes the block with the word "Abstract:" — strip that off
            if text.lower().startswith("abstract:"):
                text = text[len("abstract:"):].strip()
            return text
        # if we can't find it, fall through to the general <p> logic below as a backup

    paragraphs = soup.find_all("p")
    clean_paragraphs = [
        p.get_text().strip()
        for p in paragraphs
        if len(p.get_text().strip()) >= MIN_PARAGRAPH_LENGTH
    ]
    full_text = "\n\n".join(clean_paragraphs)
    return full_text


def fetch_all_full_texts():
    """
    Finds all articles missing full_text, extracts it, and saves it to the DB.
    """
    articles = get_articles_without_full_text()
    print(f"Found {len(articles)} articles needing full text extraction.\n")

    for article_id, title, link in articles:
        print(f"Extracting: {title[:60]}...")
        text = extract_full_text(link)

        if text:
            print(f"  Got {len(text)} characters.")
        else:
            print("  Got no usable text (will store empty string, pipeline continues).")

        update_full_text(article_id, text)

    print("\nDone extracting full text for all pending articles.")


if __name__ == "__main__":
    fetch_all_full_texts()