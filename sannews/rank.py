from __future__ import annotations

from datetime import datetime, timezone

from sannews.models import NewsItem


def score_item(item: NewsItem) -> float:
    trust = float(item.source_trust)
    hn = 0.0
    if item.hn_score is not None:
        hn += min(1.0, item.hn_score / 500.0) * 0.25
    if item.hn_comments is not None:
        hn += min(1.0, item.hn_comments / 300.0) * 0.15

    recency = 0.0
    if item.published_at is not None:
        age_hours = (datetime.now(tz=timezone.utc) - item.published_at.replace(tzinfo=timezone.utc)).total_seconds() / 3600.0
        recency = max(0.0, 1.0 - (age_hours / 48.0)) * 0.25

    return trust * 0.6 + hn + recency


def rank_items(items: list[NewsItem]) -> list[NewsItem]:
    return sorted(items, key=score_item, reverse=True)

