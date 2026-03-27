from __future__ import annotations


def summarize_postmortem(trade_date: str, issues: list[str]) -> dict[str, object]:
    return {
        "trade_date": trade_date,
        "issue_count": len(issues),
        "issues": issues,
    }
