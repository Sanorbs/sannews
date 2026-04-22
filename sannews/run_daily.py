from __future__ import annotations

import os

from dotenv import load_dotenv

from sannews.config import load_settings
from sannews.db import fetch_recent, init_db, upsert_items
from sannews.digest import format_digest
from sannews.pipeline import fetch_all, process
from sannews.sources import load_sources
from sannews.summarize import summarize_items_openai_compatible


def main() -> int:
    load_dotenv()
    settings = load_settings()

    init_db(settings.db_path)
    sources = load_sources("sources.yaml")

    fetched = fetch_all(sources, per_source_max=40)
    processed = process(fetched, max_items=settings.max_items)

    # Persist (so you can build an archive later)
    upsert_items(settings.db_path, processed)

    # Optional: also include recent items for stability (avoid empty digest)
    if not processed:
        processed = process(fetch_recent(settings.db_path, hours=72), max_items=settings.max_items)

    summaries = summarize_items_openai_compatible(
        processed,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        model=settings.openai_model,
    )
    message = format_digest(processed, summaries)

    # Dry-run if Telegram is not configured
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        print(message)
        print("\n(Delivery skipped: set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env)\n")
        return 0

    from sannews.notify import send_telegram_message

    send_telegram_message(
        bot_token=settings.telegram_bot_token,
        chat_id=settings.telegram_chat_id,
        text=message,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

