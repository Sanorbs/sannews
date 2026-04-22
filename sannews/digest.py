from __future__ import annotations

from datetime import datetime

from sannews.models import NewsItem
from sannews.summarize import SummarizeResult


def format_digest(items: list[NewsItem], summaries: SummarizeResult) -> str:
    date_str = datetime.now().strftime("%Y-%m-%d")
    lines: list[str] = [f"Verified Tech Digest - {date_str}", "", summaries.digest_intro.strip(), ""]

    for idx, it in enumerate(items, start=1):
        key = it.canonical_url or str(it.url)
        lines.append(f"{idx}) {it.title}")

        s = summaries.item_summaries.get(key)
        if s:
            lines.append(s)
        lines.append(f"Source: {it.source_name} (trust {it.source_trust:.2f})")
        if it.hn_score is not None and it.source_id.startswith("hn"):
            lines.append(f"HN: {it.hn_score} points, {it.hn_comments or 0} comments")
        lines.append(f"Link: {it.url}")
        lines.append("")

    return "\n".join(lines).strip() + "\n"

