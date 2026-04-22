from __future__ import annotations

from datetime import datetime

import feedparser

from sannews.models import NewsItem, Source


def _parse_datetime(entry: dict) -> datetime | None:
    for k in ("published_parsed", "updated_parsed"):
        t = entry.get(k)
        if t:
            try:
                return datetime(*t[:6])
            except Exception:
                pass
    return None


def fetch_rss(source: Source, max_items: int = 30) -> list[NewsItem]:
    if not source.url:
        return []
    feed = feedparser.parse(source.url)
    items: list[NewsItem] = []
    for entry in feed.entries[:max_items]:
        link = entry.get("link")
        title = entry.get("title")
        if not link or not title:
            continue
        summary = entry.get("summary") or entry.get("description")
        items.append(
            NewsItem(
                source_id=source.id,
                source_name=source.name,
                source_trust=source.trust,
                title=str(title),
                url=str(link),
                published_at=_parse_datetime(entry),
                summary_text=str(summary) if summary else None,
            )
        )
    return items

