from __future__ import annotations

from typing import Any

from src.common.models import CandidatePlan
from src.planning.candidate_ranker import rank_candidates


def generate_plan(
    run_id: str,
    candidates: list[dict[str, Any]],
    min_score: float = 60.0,
) -> list[CandidatePlan]:
    ranked = rank_candidates(candidates, min_score=min_score)
    return [
        CandidatePlan(
            symbol=item["symbol"],
            asset_type=item["asset_type"],
            score=float(item["score"]),
            notes=[f"run_id:{run_id}"],
        )
        for item in ranked
    ]
