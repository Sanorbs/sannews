from __future__ import annotations

from pathlib import Path

import yaml

from sannews.models import Source


def load_sources(path: str | Path = "sources.yaml") -> list[Source]:
    p = Path(path)
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    sources_raw = data.get("sources", []) if isinstance(data, dict) else []
    return [Source.model_validate(s) for s in sources_raw]

