from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    db_path: str
    max_items: int

    telegram_bot_token: str | None
    telegram_chat_id: str | None

    openai_api_key: str | None
    openai_base_url: str
    openai_model: str


def load_settings() -> Settings:
    db_path = os.getenv("SANNEWS_DB_PATH", "./sannews.sqlite")
    max_items = int(os.getenv("SANNEWS_MAX_ITEMS", "10"))

    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN") or None
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID") or None

    openai_api_key = os.getenv("OPENAI_API_KEY") or None
    openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    return Settings(
        db_path=db_path,
        max_items=max_items,
        telegram_bot_token=telegram_bot_token,
        telegram_chat_id=telegram_chat_id,
        openai_api_key=openai_api_key,
        openai_base_url=openai_base_url,
        openai_model=openai_model,
    )

