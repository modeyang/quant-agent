from __future__ import annotations

from src.common.models import ReviewSummary


def build_trade_review(
    trade_date: str,
    planned: int,
    executed: int,
    rejected: int,
) -> ReviewSummary:
    notes: list[str] = []
    if executed < planned:
        notes.append(f"plan gap: executed {executed} of {planned} planned actions")
    if rejected:
        notes.append(f"rejected orders: {rejected}")

    return ReviewSummary(
        trade_date=trade_date,
        planned_count=planned,
        executed_count=executed,
        rejected_count=rejected,
        notes=notes,
    )
