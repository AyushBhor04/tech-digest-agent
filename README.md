# Tech Digest Agent

An automated daily agent that scans tech news sources, summarizes the top stories with a locally-run LLM, and emails a clean digest. It runs on free tools only: no paid APIs and no cloud hosting.

## How it works

```mermaid
flowchart TD
    T(["Windows Task Scheduler<br/>daily at 2 PM, catches up if missed"]):::trigger

    subgraph COLLECT["1 · COLLECT"]
        A["RSS feeds<br/>Hacker News, TechCrunch, arXiv CS"]:::source
        B["Keep top 2 per source<br/>fetch.py"]:::step
        C[("SQLite<br/>unique URL = dedup<br/>db.py")]:::store
    end

    subgraph PROCESS["2 · PROCESS"]
        D["Extract article text<br/>requests + BeautifulSoup<br/>fetch_full_text.py"]:::step
        E["Medium summary from full text<br/>Ollama llama3.2:3b<br/>summarize.py"]:::llm
    end

    subgraph DELIVER["3 · DELIVER"]
        F["Build HTML digest<br/>compose_email.py"]:::step
        G["Send via Gmail SMTP<br/>send_email.py"]:::step
        H(["Inbox"]):::output
    end

    T --> A --> B --> C
    C --> D --> E --> F --> G --> H
    G -.->|"sent = 1"| C

    classDef trigger fill:#fde68a,stroke:#b45309,color:#1f2937
    classDef source fill:#dbeafe,stroke:#1d4ed8,color:#1f2937
    classDef step fill:#e5e7eb,stroke:#4b5563,color:#1f2937
    classDef store fill:#dcfce7,stroke:#15803d,color:#1f2937
    classDef llm fill:#ede9fe,stroke:#6d28d9,color:#1f2937
    classDef output fill:#fecaca,stroke:#b91c1c,color:#1f2937
```

1. **Fetch:** reads RSS feeds from Hacker News, TechCrunch and arXiv CS and keeps the top 2 from each source (6 articles a day).
2. **Store:** saves articles in SQLite. The article URL is a unique key, so re-running never creates duplicates.
3. **Extract:** downloads each new article page and pulls out the readable text.
4. **Summarize:** a local LLM writes one medium-length summary from the article text.
5. **Send:** builds an HTML email and sends it through Gmail SMTP, then marks those articles as sent so they never appear twice.

## Stack

- Python 3.14
- `feedparser` for RSS, `requests` and `BeautifulSoup` for page text
- SQLite for storage
- Ollama with `llama3.2:3b` for local summarization
- Gmail SMTP with an App Password for delivery
- Windows Task Scheduler for daily automation

## Setup

1. Install Python, [Ollama](https://ollama.com), and pull the model:
   ```
   ollama pull llama3.2:3b
   ```
2. Install dependencies:
   ```
   pip install feedparser requests beautifulsoup4 python-dotenv
   ```
3. Create a `.env` file in the project folder (it is gitignored):
   ```
   GMAIL_ADDRESS=your_address@gmail.com
   GMAIL_APP_PASSWORD=your_16_character_app_password
   ```
4. Run the whole pipeline once:
   ```
   python main.py
   ```
5. For daily automation, create a Windows Task Scheduler task that runs `python.exe main.py` with the project folder as the "Start in" directory. Enable "Run task as soon as possible after a scheduled start is missed" so a day when the laptop was off is caught up at the next login.

## Project structure

| File | Role |
|---|---|
| `fetch.py` | Reads RSS feeds, keeps the top N per source |
| `db.py` | SQLite schema and all database queries |
| `fetch_full_text.py` | Extracts article text from each page |
| `summarize.py` | Generates summaries through the Ollama API |
| `compose_email.py` | Builds the HTML digest |
| `send_email.py` | Sends the digest and marks articles as sent |
| `main.py` | Runs every stage in order, with per-stage error handling |

## Design decisions

- **Local LLM instead of a hosted API:** zero cost, no rate limits, and article text stays on my machine. I benchmarked `mistral` (about 2 minutes per response) against `llama3.2:3b` (about 7 seconds for short prompts) and chose the smaller model.
- **Summarize from full text, not headlines:** an early version summarized headlines alone, and the model invented details. Summaries are now generated from the article text, with an instruction to use only that text.
- **Top 2 per source:** unbounded fetching is impractical (arXiv alone returns over a thousand entries a day). Taking the top 2 from each source gives a balanced mix of 6 articles, and it cut a full run from about 30 minutes to a few minutes.
- **Retrieve, then generate:** each article's stored text is retrieved from SQLite and passed to the model as context, so the summary is grounded in the source. Input is capped at 4,000 characters to fit the small model's context window.
- **Idempotent pipeline:** a UNIQUE constraint on the URL and a `sent` flag mean the pipeline can run any number of times a day without duplicate rows or duplicate emails.
- **Fault isolation:** every stage in `main.py` is wrapped separately, so one failure (for example, a site that blocks scraping) does not stop the rest of the run.
- **Task Scheduler instead of GitHub Actions:** cloud runners cannot reach a local Ollama instance. A missed run is caught up the next time the laptop is on.

## Known limitations

- **Text extraction is a heuristic.** It collects paragraph tags, which works on most news sites but fails on JavaScript-rendered pages and on sites that block scrapers. Articles with no extractable text are skipped. arXiv gets a special case because its abstract is not in a normal paragraph tag.
- **A 3B model can misread technical content.** Summaries are usually accurate, but occasional errors occur.
- **arXiv publishes nothing on weekends,** so Saturday and Sunday digests have no arXiv section.
- **Gmail does not support collapsible `<details>` sections.** The first version used them for a long summary, and Gmail showed them expanded. I replaced the two-level summary with a single medium one.
- **The laptop must be on and awake while the pipeline runs.**

## Planned improvements

- Rank candidate articles with an LLM relevance score instead of fixed top-2 sampling
- Tighter control of summary length and quality
- Fall back to the next candidate when an article cannot be extracted