from __future__ import annotations

from typing import Any


def assess_auction_snapshot(snapshot: dict[str, Any] | None) -> dict[str, Any]:
    if not snapshot:
        return {
            "status": "pending",
            "summary": "auction snapshot unavailable",
            "imbalance_ratio": 0.0,
        }

    imbalance_ratio = float(snapshot.get("imbalance_ratio", 0.0))
    if imbalance_ratio >= 1.2:
        status = "reinforced"
    elif imbalance_ratio >= 0.8:
        status = "neutral"
    else:
        status = "weakened"

    return {
        "status": status,
        "summary": f"auction imbalance ratio={imbalance_ratio:.2f}",
        "imbalance_ratio": imbalance_ratio,
    }

