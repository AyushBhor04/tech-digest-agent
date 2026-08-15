# Tech Digest Agent

An automated daily digest agent that scans tech news sources (Hacker News, TechCrunch, arXiv), summarizes articles using a locally-run LLM (Ollama), and emails a digest with quick + optional detailed summaries per story.

## Status
🚧 Work in progress — built as a learning/resume project.

## Stack
- Python
- RSS (feedparser) for sourcing
- SQLite for storage
- Ollama (local LLM) for summarization
- SMTP (Gmail) for email delivery
- Cron for scheduling
