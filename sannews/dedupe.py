from __future__ import annotations

import hashlib
import re
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from rapidfuzz import fuzz

from sannews.models import NewsItem


_TRACKING_QUERY_KEYS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "utm_id",
    "utm_reader",
    "gclid",
    "fbclid",
    "mc_cid",
    "mc_eid",
    "ref",
    "src",
}


def canonicalize_url(url: str) -> str:
    p = urlparse(url)
    query = [(k, v) for (k, v) in parse_qsl(p.query, keep_blank_values=True) if k.lower() not in _TRACKING_QUERY_KEYS]
    query.sort()
    cleaned = p._replace(
        scheme=p.scheme.lower() or "https",
        netloc=p.netloc.lower(),
        fragment="",
        query=urlencode(query, doseq=True),
    )
    return urlunparse(cleaned)


def normalize_title(title: str) -> str:
    t = title.strip().lower()
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"[“”]", '"', t)
    t = re.sub(r"[’]", "'", t)
    return t


def content_fingerprint(title: str, canonical_url: str) -> str:
    h = hashlib.sha256()
    h.update(normalize_title(title).encode("utf-8"))
    h.update(b"\n")
    h.update(canonical_url.encode("utf-8"))
    return h.hexdigest()[:24]


def dedupe_items(items: list[NewsItem], title_threshold: int = 92) -> list[NewsItem]:
    """
    Dedupe by:
    - canonical URL exact match
    - near-duplicate title match (high threshold) across different URLs
    """
    seen_urls: set[str] = set()
    winners: list[NewsItem] = []

    for it in items:
        it.canonical_url = canonicalize_url(str(it.url))
        it.content_hash = content_fingerprint(it.title, it.canonical_url)

    for it in sorted(items, key=lambda x: (x.source_trust, x.hn_score or 0), reverse=True):
        if it.canonical_url and it.canonical_url in seen_urls:
            continue

        is_dup = False
        t = normalize_title(it.title)
        for kept in winners:
            if fuzz.ratio(t, normalize_title(kept.title)) >= title_threshold:
                is_dup = True
                break

        if is_dup:
            continue

        seen_urls.add(it.canonical_url or str(it.url))
        winners.append(it)

    return winners

