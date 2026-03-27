from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from src.data.runtime import ResearchRuntime, build_research_runtime
from src.planning.signal_engine import score_candidate
from src.planning.plan_generator import generate_plan


def _default_db_path() -> Path:
    return Path("data/db/quant-agent.sqlite3")


def _load_min_score(default: float = 60.0) -> float:
    config_path = Path("config/strategy.yaml")
    if not config_path.exists():
        return default

    with config_path.open("r", encoding="utf-8") as file:
        raw = yaml.safe_load(file) or {}

    return float(raw.get("planning", {}).get("thresholds", {}).get("candidate_min_score", default))


def _derive_candidates(bars: list[Any]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for bar in bars:
        change_pct = ((bar.close - bar.open) / bar.open) * 100 if bar.open else 0.0
        event_score = 70.0
        trend_score = min(100.0, max(0.0, 50.0 + change_pct * 10))
        flow_score = min(100.0, 50.0 + min(bar.volume / 10000.0, 50.0))
        total_score = score_candidate(
            event_score=event_score,
            trend_score=trend_score,
            flow_score=flow_score,
            weights={"event": 0.4, "trend": 0.3, "flow": 0.3},
        )
        candidates.append(
            {
                "symbol": bar.symbol,
                "asset_type": "stock",
                "score": total_score,
            }
        )
    return candidates


def _serialize_plans(plans: list[Any]) -> list[dict[str, Any]]:
    return [
        {
            "symbol": plan.symbol,
            "asset_type": plan.asset_type,
            "score": plan.score,
            "status": plan.status,
            "notes": plan.notes,
        }
        for plan in plans
    ]

def run_p0_cycle(
    mode: str = "plan_only",
    runtime: ResearchRuntime | None = None,
    symbols: list[str] | None = None,
    start: str = "2026-03-01",
    end: str = "2026-03-27",
    min_score: float | None = None,
) -> dict[str, Any]:
    try:
        resolved_runtime = runtime or build_research_runtime(_default_db_path())
    except ModuleNotFoundError as exc:
        return {
            "planning": {
                "status": "unavailable",
                "reason": f"missing dependency: {exc.name}",
                "plan_count": 0,
                "plans": [],
            },
            "execution": {"status": "skipped" if mode == "plan_only" else "pending"},
            "review": {"status": "pending", "summary": "review not executed"},
        }
    resolved_symbols = symbols or ["600000.SH"]
    resolved_min_score = min_score if min_score is not None else _load_min_score()
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")

    bars = resolved_runtime.provider.get_daily_bars(resolved_symbols, start, end)
    candidates = _derive_candidates(bars)
    plans = generate_plan(run_id=run_id, candidates=candidates, min_score=resolved_min_score)
    resolved_runtime.plan_repo.save_candidate_plans(run_id, plans)

    return {
        "planning": {
            "status": "ready",
            "run_id": run_id,
            "plan_count": len(plans),
            "plans": _serialize_plans(plans),
            "min_score": resolved_min_score,
            "db_path": str(resolved_runtime.db_path),
        },
        "execution": {"status": "skipped" if mode == "plan_only" else "pending"},
        "review": {"status": "pending", "summary": "review not executed in plan_only mode"},
    }
