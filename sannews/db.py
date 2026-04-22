from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from sannews.models import NewsItem


SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  canonical_url TEXT NOT NULL UNIQUE,
  url TEXT NOT NULL,
  title TEXT NOT NULL,
  source_id TEXT NOT NULL,
  source_name TEXT NOT NULL,
  source_trust REAL NOT NULL,
  published_at TEXT,
  summary_text TEXT,
  hn_score INTEGER,
  hn_comments INTEGER,
  content_hash TEXT,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_items_created_at ON items(created_at);
CREATE INDEX IF NOT EXISTS idx_items_published_at ON items(published_at);
"""


def init_db(db_path: str) -> None:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.executescript(SCHEMA)


@contextmanager
def connect(db_path: str):
    conn = sqlite3.connect(db_path)
    try:
        yield conn
    finally:
        conn.close()


def upsert_items(db_path: str, items: list[NewsItem]) -> int:
    if not items:
        return 0
    now = datetime.utcnow().isoformat()
    rows = 0
    with connect(db_path) as conn:
        cur = conn.cursor()
        for it in items:
            published_at = it.published_at.isoformat() if it.published_at else None
            try:
                cur.execute(
                    """
                    INSERT OR IGNORE INTO items
                      (canonical_url, url, title, source_id, source_name, source_trust,
                       published_at, summary_text, hn_score, hn_comments, content_hash, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        it.canonical_url or str(it.url),
                        str(it.url),
                        it.title,
                        it.source_id,
                        it.source_name,
                        float(it.source_trust),
                        published_at,
                        it.summary_text,
                        it.hn_score,
                        it.hn_comments,
                        it.content_hash,
                        now,
                    ),
                )
                rows += cur.rowcount
            except sqlite3.Error:
                continue
        conn.commit()
    return rows


def fetch_recent(db_path: str, hours: int = 36) -> list[NewsItem]:
    cutoff = datetime.utcnow().timestamp() - hours * 3600
    cutoff_iso = datetime.utcfromtimestamp(cutoff).isoformat()
    with connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT canonical_url, url, title, source_id, source_name, source_trust,
                   published_at, summary_text, hn_score, hn_comments, content_hash
            FROM items
            WHERE created_at >= ?
            ORDER BY COALESCE(published_at, created_at) DESC
            """,
            (cutoff_iso,),
        )
        rows = cur.fetchall()

    items: list[NewsItem] = []
    for canonical_url, url, title, source_id, source_name, source_trust, published_at, summary_text, hn_score, hn_comments, content_hash in rows:
        dt = datetime.fromisoformat(published_at) if published_at else None
        items.append(
            NewsItem(
                source_id=source_id,
                source_name=source_name,
                source_trust=float(source_trust),
                title=title,
                url=url,
                published_at=dt,
                summary_text=summary_text,
                hn_score=hn_score,
                hn_comments=hn_comments,
                canonical_url=canonical_url,
                content_hash=content_hash,
            )
        )
    return items

