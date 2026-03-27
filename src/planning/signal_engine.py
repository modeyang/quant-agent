from __future__ import annotations


def score_candidate(
    event_score: float,
    trend_score: float,
    flow_score: float,
    weights: dict[str, float],
) -> float:
    return round(
        event_score * weights["event"]
        + trend_score * weights["trend"]
        + flow_score * weights["flow"],
        2,
    )
