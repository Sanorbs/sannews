from __future__ import annotations

from sannews.dedupe import dedupe_items
from sannews.fetchers import fetch_hn_top, fetch_rss
from sannews.models import NewsItem, Source
from sannews.rank import rank_items


def fetch_all(sources: list[Source], per_source_max: int = 30) -> list[NewsItem]:
    items: list[NewsItem] = []
    for src in sources:
        if src.type == "rss":
            items.extend(fetch_rss(src, max_items=per_source_max))
        elif src.type == "hn_top":
            items.extend(fetch_hn_top(src, max_items=per_source_max))
    return items


def process(items: list[NewsItem], max_items: int) -> list[NewsItem]:
    items = dedupe_items(items)
    items = rank_items(items)
    return items[:max_items]

