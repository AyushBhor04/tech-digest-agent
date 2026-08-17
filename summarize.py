import requests
from db import get_articles_without_summary, update_summary

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:3b"


def generate_summary(title):
    prompt = prompt = (
        f"Headline: \"{title}\"\n\n"
        "Write a 2-3 sentence plain-language summary explaining what this headline likely means. "
        "Do not include any preamble, introduction, or phrases like 'Here is a summary'. "
        "Respond with ONLY the summary text itself, starting directly with the first sentence."
    )

    response = requests.post(OLLAMA_URL, json={
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    })

    response.raise_for_status()  # raises an error if the request failed
    data = response.json()
    return data["response"].strip()


def summarize_pending_articles():
    articles = get_articles_without_summary()
    print(f"Found {len(articles)} articles needing summaries.")

    for article_id, title, link in articles:
        print(f"\nSummarizing (id={article_id}): {title}")
        try:
            summary = generate_summary(title)
            update_summary(article_id, summary)
            print(f"  -> {summary}")
        except requests.exceptions.RequestException as e:
            print(f"  ERROR: Could not reach Ollama. Is it running? Details: {e}")


if __name__ == "__main__":
    summarize_pending_articles()