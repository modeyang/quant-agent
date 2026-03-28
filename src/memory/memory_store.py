from __future__ import annotations

from typing import Any

from src.memory.event_gate import gate_memory_score, should_persist


def _clamp(score: float) -> float:
    return max(0.0, min(1.0, score))


def build_trade_memory_entries(
    run_id: str,
    review_payload: dict[str, Any],
    monitoring_payload: dict[str, Any],
) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []

    if review_payload.get("status") == "ready":
        planned = int(review_payload.get("planned_count", 0))
        executed = int(review_payload.get("executed_count", 0))
        rejected = int(review_payload.get("rejected_count", 0))

        if planned == 0:
            score = 0.7
        else:
            score = _clamp(executed / planned - rejected * 0.1)

        status = gate_memory_score(score)
        if should_persist(score):
            entries.append(
                {
                    "run_id": run_id,
                    "memory_type": "trade_memory",
                    "symbol": None,
                    "title": f"trade review {review_payload.get('trade_date', 'unknown')}",
                    "content": (
                        f"planned={planned}, executed={executed}, rejected={rejected}, "
                        f"notes={review_payload.get('notes', [])}"
                    ),
                    "score": round(score, 4),
                    "status": status,
                }
            )

    if monitoring_payload.get("status") in {"alert", "reinforced"}:
        score = 0.9 if monitoring_payload["status"] == "reinforced" else 0.7
        status = gate_memory_score(score)
        if should_persist(score):
            entries.append(
                {
                    "run_id": run_id,
                    "memory_type": "market_memory",
                    "symbol": None,
                    "title": f"monitoring {monitoring_payload['status']}",
                    "content": (
                        f"invalidated={monitoring_payload.get('invalidated_symbols', [])}, "
                        f"reinforced={monitoring_payload.get('reinforced_symbols', [])}"
                    ),
                    "score": score,
                    "status": status,
                }
            )

    return entries

