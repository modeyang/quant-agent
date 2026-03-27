from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from src.data.runtime import ResearchRuntime, build_research_runtime
from src.execution.approval import require_manual_approval
from src.execution.order_state_machine import OrderStateMachine
from src.execution.reconcile import reconcile_run
from src.planning.plan_generator import generate_plan
from src.planning.signal_engine import score_candidate
from src.review.postmortem import summarize_postmortem
from src.review.trade_review import build_trade_review


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


def _make_order_intent(symbol: str, quantity: int = 100, price: float | None = None) -> dict[str, Any]:
    return {
        "symbol": symbol,
        "side": "buy",
        "quantity": quantity,
        "price_type": "limit",
        "price": price,
    }


def _execute_cycle(
    runtime: ResearchRuntime,
    run_id: str,
    plans: list[Any],
    broker: Any | None,
    approval_granted: bool,
    trade_date: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if not plans:
        review = build_trade_review(
            trade_date=trade_date,
            planned=0,
            executed=0,
            rejected=0,
        )
        return (
            {
                "status": "skipped",
                "reason": "no candidate plans",
                "order_count": 0,
                "fill_count": 0,
                "reconciled_count": 0,
                "rejected_count": 0,
                "blocked_count": 0,
                "unmatched_order_ids": [],
            },
            {
                "status": "ready",
                "trade_date": trade_date,
                "planned_count": review.planned_count,
                "executed_count": review.executed_count,
                "rejected_count": review.rejected_count,
                "notes": review.notes,
                "postmortem": summarize_postmortem(trade_date, []),
            },
        )

    if broker is None:
        return (
            {
                "status": "unavailable",
                "reason": "missing broker for execute mode",
                "order_count": 0,
                "fill_count": 0,
                "reconciled_count": 0,
                "rejected_count": len(plans),
                "blocked_count": 0,
                "unmatched_order_ids": [],
            },
            {
                "status": "pending",
                "summary": "review skipped because execution broker is unavailable",
            },
        )

    executed_count = 0
    rejected_count = 0
    blocked_count = 0

    for idx, plan in enumerate(plans, start=1):
        order_id = f"{run_id}-O{idx:03d}"
        intent = _make_order_intent(symbol=plan.symbol)

        if require_manual_approval("open", approval_granted):
            blocked_count += 1
            rejected_count += 1
            runtime.order_repo.save_order(
                run_id=run_id,
                order_id=order_id,
                symbol=plan.symbol,
                side=intent["side"],
                quantity=intent["quantity"],
                price=intent["price"],
                status="rejected",
            )
            continue

        state_machine = OrderStateMachine(plan_id=plan.symbol)
        state_machine.approve()
        state_machine.submit()
        runtime.order_repo.save_order(
            run_id=run_id,
            order_id=order_id,
            symbol=plan.symbol,
            side=intent["side"],
            quantity=intent["quantity"],
            price=intent["price"],
            status=state_machine.state,
        )

        try:
            broker.place_order(intent)
            state_machine.fill()
            runtime.order_repo.update_status(order_id=order_id, status=state_machine.state)
            runtime.fill_repo.save_fill(
                run_id=run_id,
                fill_id=f"{order_id}-F001",
                order_id=order_id,
                symbol=plan.symbol,
                quantity=intent["quantity"],
                price=float(intent["price"] or 0.0),
                filled_at=f"{trade_date} 14:50:00",
            )
            state_machine.reconcile()
            runtime.order_repo.update_status(order_id=order_id, status=state_machine.state)
            executed_count += 1
        except Exception:
            state_machine.reject()
            runtime.order_repo.update_status(order_id=order_id, status=state_machine.state)
            rejected_count += 1

    orders = runtime.order_repo.list_by_run(run_id)
    fills = runtime.fill_repo.list_by_run(run_id)
    reconcile_summary = reconcile_run(
        orders=[{"order_id": item["order_id"], "status": item["status"]} for item in orders],
        fills=[{"order_id": item["order_id"], "qty": item["quantity"]} for item in fills],
    )
    runtime.account_snapshot_repo.save_snapshot(
        run_id=run_id,
        cash=0.0,
        total_asset=float(len(orders)),
        position_value=float(executed_count),
        snapshot_at=f"{trade_date} 15:00:00",
    )

    review = build_trade_review(
        trade_date=trade_date,
        planned=len(plans),
        executed=executed_count,
        rejected=rejected_count,
    )
    postmortem_issues: list[str] = []
    if blocked_count:
        postmortem_issues.append(f"blocked orders: {blocked_count}")
    if reconcile_summary["unmatched_order_ids"]:
        postmortem_issues.append(
            f"unmatched orders: {', '.join(reconcile_summary['unmatched_order_ids'])}"
        )

    execution_status = "done"
    if blocked_count and executed_count == 0:
        execution_status = "blocked"

    execution = {
        "status": execution_status,
        "order_count": len(orders),
        "fill_count": len(fills),
        "reconciled_count": reconcile_summary["reconciled"],
        "rejected_count": rejected_count,
        "blocked_count": blocked_count,
        "unmatched_order_ids": reconcile_summary["unmatched_order_ids"],
    }
    review_payload = {
        "status": "ready",
        "trade_date": trade_date,
        "planned_count": review.planned_count,
        "executed_count": review.executed_count,
        "rejected_count": review.rejected_count,
        "notes": review.notes,
        "postmortem": summarize_postmortem(trade_date, postmortem_issues),
    }
    return execution, review_payload


def run_p0_cycle(
    mode: str = "plan_only",
    runtime: ResearchRuntime | None = None,
    symbols: list[str] | None = None,
    start: str = "2026-03-01",
    end: str = "2026-03-27",
    min_score: float | None = None,
    broker: Any | None = None,
    approval_granted: bool = False,
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

    resolved_runtime.run_log_repo.start_run(
        run_id=run_id,
        mode=mode,
        status="running",
        message="cycle started",
    )

    try:
        bars = resolved_runtime.provider.get_daily_bars(resolved_symbols, start, end)
        candidates = _derive_candidates(bars)
        plans = generate_plan(run_id=run_id, candidates=candidates, min_score=resolved_min_score)
        resolved_runtime.plan_repo.save_candidate_plans(run_id, plans)

        if mode == "plan_only":
            execution_payload = {
                "status": "skipped",
                "reason": "plan_only mode",
                "order_count": 0,
                "fill_count": 0,
                "reconciled_count": 0,
                "rejected_count": 0,
                "blocked_count": 0,
                "unmatched_order_ids": [],
            }
            review_payload: dict[str, Any] = {
                "status": "pending",
                "summary": "review not executed in plan_only mode",
            }
        else:
            execution_payload, review_payload = _execute_cycle(
                runtime=resolved_runtime,
                run_id=run_id,
                plans=plans,
                broker=broker,
                approval_granted=approval_granted,
                trade_date=end,
            )

        run_status = "success"
        if execution_payload["status"] in {"unavailable", "failed"}:
            run_status = "failed"
        resolved_runtime.run_log_repo.finish_run(
            run_id=run_id,
            status=run_status,
            message=execution_payload.get("reason", execution_payload["status"]),
        )
        run_record = resolved_runtime.run_log_repo.get_by_run(run_id)

        return {
            "planning": {
                "status": "ready",
                "run_id": run_id,
                "plan_count": len(plans),
                "plans": _serialize_plans(plans),
                "min_score": resolved_min_score,
                "db_path": str(resolved_runtime.db_path),
            },
            "execution": execution_payload,
            "review": review_payload,
            "run": run_record,
        }
    except Exception as exc:
        resolved_runtime.run_log_repo.finish_run(
            run_id=run_id,
            status="failed",
            message=str(exc),
        )
        run_record = resolved_runtime.run_log_repo.get_by_run(run_id)
        return {
            "planning": {
                "status": "failed",
                "run_id": run_id,
                "reason": str(exc),
                "plan_count": 0,
                "plans": [],
            },
            "execution": {"status": "failed", "reason": str(exc)},
            "review": {"status": "failed", "summary": "review skipped because run failed"},
            "run": run_record,
        }
