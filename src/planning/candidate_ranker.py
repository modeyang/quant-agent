from __future__ import annotations

from typing import Any


def rank_candidates(
    candidates: list[dict[str, Any]],
    min_score: float = 0.0,
) -> list[dict[str, Any]]:
    filtered = [candidate for candidate in candidates if candidate["score"] >= min_score]
    return sorted(filtered, key=lambda item: item["score"], reverse=True)
