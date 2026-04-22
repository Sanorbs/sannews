# sannews — verified tech news digest (MVP)

Daily pipeline:

1) Fetch from trusted sources (RSS + Hacker News)
2) Normalize + store
3) Deduplicate + rank
4) Summarize (local fallback; optional OpenAI-compatible)
5) Send digest (Telegram)

## Quick start (Windows / PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

Copy-Item .env.example .env
notepad .env

python -m sannews.run_daily
```

## Configure sources

- Edit `sources.yaml` to add/remove trusted RSS feeds and adjust `trust` scores.

## Environment variables

- `TELEGRAM_BOT_TOKEN`: your bot token from BotFather
- `TELEGRAM_CHAT_ID`: your chat id (or a group id)
- `SANNEWS_DB_PATH` (optional): defaults to `./sannews.sqlite`
- `SANNEWS_MAX_ITEMS` (optional): defaults to 10

Optional AI summarization (OpenAI-compatible HTTP API):

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL` (optional): defaults to `https://api.openai.com/v1`
- `OPENAI_MODEL` (optional): defaults to `gpt-4o-mini`

If OpenAI vars aren’t set, the MVP uses a deterministic non-AI summary (title + source + link).

## Run daily automatically

Simplest: Windows Task Scheduler runs:

```powershell
cd C:\Users\sande\OneDrive\Desktop\sannews
.\.venv\Scripts\python.exe -m sannews.run_daily
```

