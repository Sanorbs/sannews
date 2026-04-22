from __future__ import annotations

import json
from dataclasses import dataclass

import requests

from sannews.models import NewsItem


@dataclass(frozen=True)
class SummarizeResult:
    item_summaries: dict[str, str]  # canonical_url -> summary
    digest_intro: str


def _fallback_summaries(items: list[NewsItem]) -> SummarizeResult:
    item_summaries: dict[str, str] = {}
    for it in items:
        key = it.canonical_url or str(it.url)
        item_summaries[key] = f"{it.title} ({it.source_name})"
    intro = "Today's verified tech digest (trusted sources; deduped)."
    return SummarizeResult(item_summaries=item_summaries, digest_intro=intro)


def _openai_chat(
    *,
    api_key: str,
    base_url: str,
    model: str,
    user_prompt: str,
    timeout_s: int = 45,
) -> str:
    url = f"{base_url}/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You write concise, factual tech news digests."},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
    }
    r = requests.post(
        url,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        data=json.dumps(payload),
        timeout=timeout_s,
    )
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"].strip()


def summarize_items_openai_compatible(
    items: list[NewsItem],
    *,
    api_key: str | None,
    base_url: str,
    model: str,
) -> SummarizeResult:
    if not api_key:
        return _fallback_summaries(items)

    # Keep prompts short to avoid huge token usage.
    lines = []
    for i, it in enumerate(items, start=1):
        key = it.canonical_url or str(it.url)
        lines.append(
            f"{i}. [{it.source_name} | trust={it.source_trust:.2f}] {it.title}\nURL: {it.url}\nKEY: {key}"
        )

    prompt = (
        "Create a daily tech digest.\n\n"
        "Rules:\n"
        "- For each item, produce 2 bullets: (a) what happened (b) why it matters.\n"
        "- Be factual; do not invent details not in the title.\n"
        "- Keep each item to <= 35 words.\n"
        "- Output JSON only with shape:\n"
        '  {"intro": "...", "items": [{"key": "...", "bullets": ["...", "..."]}]}\n\n'
        "Items:\n"
        + "\n\n".join(lines)
    )

    text = _openai_chat(api_key=api_key, base_url=base_url, model=model, user_prompt=prompt)
    try:
        parsed = json.loads(text)
        intro = str(parsed.get("intro") or "Today’s verified tech digest.")
        item_summaries: dict[str, str] = {}
        for row in parsed.get("items", []):
            key = str(row.get("key") or "")
            bullets = row.get("bullets") or []
            bullets = [str(b).strip() for b in bullets if str(b).strip()]
            if key and bullets:
                item_summaries[key] = "\n".join([f"- {b}" for b in bullets[:2]])
        if not item_summaries:
            return _fallback_summaries(items)
        return SummarizeResult(item_summaries=item_summaries, digest_intro=intro)
    except Exception:
        return _fallback_summaries(items)

