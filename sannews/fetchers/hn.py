from __future__ import annotations

from datetime import datetime

import requests

from sannews.models import NewsItem, Source


HN_BASE = "https://hacker-news.firebaseio.com/v0"


def fetch_hn_top(source: Source, max_items: int = 30) -> list[NewsItem]:
    try:
        top = requests.get(f"{HN_BASE}/topstories.json", timeout=15)
        top.raise_for_status()
        ids: list[int] = top.json()[:max_items]
    except Exception:
        return []

    items: list[NewsItem] = []
    for story_id in ids:
        try:
            r = requests.get(f"{HN_BASE}/item/{story_id}.json", timeout=15)
            r.raise_for_status()
            data = r.json()
        except Exception:
            continue

        if not isinstance(data, dict):
            continue
        if data.get("type") != "story":
            continue
        if not data.get("url") or not data.get("title"):
            continue

        published_at = None
        if data.get("time"):
            try:
                published_at = datetime.utcfromtimestamp(int(data["time"]))
            except Exception:
                published_at = None

        items.append(
            NewsItem(
                source_id=source.id,
                source_name=source.name,
                source_trust=source.trust,
                title=str(data["title"]),
                url=str(data["url"]),
                published_at=published_at,
                summary_text=None,
                hn_score=int(data.get("score") or 0),
                hn_comments=int(data.get("descendants") or 0),
            )
        )
    return items

