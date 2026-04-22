from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


SourceType = Literal["rss", "hn_top"]


class Source(BaseModel):
    id: str
    name: str
    type: SourceType
    url: str | None = None
    trust: float = Field(ge=0.0, le=1.0, default=0.8)
    tags: list[str] = Field(default_factory=list)


class NewsItem(BaseModel):
    source_id: str
    source_name: str
    source_trust: float

    title: str
    url: HttpUrl
    published_at: datetime | None = None
    summary_text: str | None = None  # short snippet from feed/API

    # Signals (optional)
    hn_score: int | None = None
    hn_comments: int | None = None

    # Derived
    canonical_url: str | None = None
    content_hash: str | None = None

