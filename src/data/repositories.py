from __future__ import annotations

import sqlite3
from typing import Any

from src.common.models import CandidatePlan


class PlanRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def save_plan(
        self,
        run_id: str,
        symbol: str,
        asset_type: str,
        score: float,
        status: str = "planned",
    ) -> None:
        self.conn.execute(
            """
            insert into candidate_plan (run_id, symbol, asset_type, score, status)
            values (?, ?, ?, ?, ?)
            on conflict(run_id, symbol) do update set
                asset_type = excluded.asset_type,
                score = excluded.score,
                status = excluded.status
            """,
            (run_id, symbol, asset_type, score, status),
        )
        self.conn.commit()

    def list_by_run(self, run_id: str) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            select id, run_id, symbol, asset_type, score, status, created_at
            from candidate_plan
            where run_id = ?
            order by id asc
            """,
            (run_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    def save_candidate_plans(self, run_id: str, plans: list[CandidatePlan]) -> None:
        for plan in plans:
            self.save_plan(
                run_id=run_id,
                symbol=plan.symbol,
                asset_type=plan.asset_type,
                score=plan.score,
                status=plan.status,
            )
