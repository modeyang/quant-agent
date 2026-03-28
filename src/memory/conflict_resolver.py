from __future__ import annotations

from typing import Any


def resolve_memory_conflicts(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: dict[tuple[str, str, str | None], dict[str, Any]] = {}
    for entry in entries:
        key = (entry["memory_type"], entry["title"], entry.get("symbol"))
        existing = deduped.get(key)
        if existing is None or float(entry["score"]) > float(existing["score"]):
            deduped[key] = entry
    return list(deduped.values())

