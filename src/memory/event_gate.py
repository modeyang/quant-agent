from __future__ import annotations

CONFIRMED_THRESHOLD = 0.85
PROVISIONAL_THRESHOLD = 0.65


def gate_memory_score(score: float) -> str:
    if score >= CONFIRMED_THRESHOLD:
        return "confirmed"
    if score >= PROVISIONAL_THRESHOLD:
        return "provisional"
    return "rejected"


def should_persist(score: float) -> bool:
    return score >= PROVISIONAL_THRESHOLD

