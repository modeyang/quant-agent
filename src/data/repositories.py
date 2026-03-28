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


class RunLogRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def start_run(
        self,
        run_id: str,
        mode: str,
        status: str = "running",
        message: str | None = None,
    ) -> None:
        self.conn.execute(
            """
            insert into run_log (run_id, mode, status, message)
            values (?, ?, ?, ?)
            on conflict(run_id) do update set
                mode = excluded.mode,
                status = excluded.status,
                message = excluded.message,
                finished_at = null
            """,
            (run_id, mode, status, message),
        )
        self.conn.commit()

    def finish_run(
        self,
        run_id: str,
        status: str,
        message: str | None = None,
    ) -> None:
        self.conn.execute(
            """
            update run_log
            set status = ?, message = ?, finished_at = current_timestamp
            where run_id = ?
            """,
            (status, message, run_id),
        )
        self.conn.commit()

    def get_by_run(self, run_id: str) -> dict[str, Any] | None:
        row = self.conn.execute(
            """
            select id, run_id, mode, status, message, started_at, finished_at
            from run_log
            where run_id = ?
            """,
            (run_id,),
        ).fetchone()
        if row is None:
            return None
        return dict(row)


class OrderRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def save_order(
        self,
        run_id: str,
        order_id: str,
        symbol: str,
        side: str,
        quantity: int,
        price: float | None,
        status: str,
    ) -> None:
        self.conn.execute(
            """
            insert into orders (run_id, order_id, symbol, side, quantity, price, status)
            values (?, ?, ?, ?, ?, ?, ?)
            on conflict(order_id) do update set
                run_id = excluded.run_id,
                symbol = excluded.symbol,
                side = excluded.side,
                quantity = excluded.quantity,
                price = excluded.price,
                status = excluded.status
            """,
            (run_id, order_id, symbol, side, quantity, price, status),
        )
        self.conn.commit()

    def update_status(self, order_id: str, status: str) -> None:
        self.conn.execute(
            "update orders set status = ? where order_id = ?",
            (status, order_id),
        )
        self.conn.commit()

    def list_by_run(self, run_id: str) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            select id, run_id, order_id, symbol, side, quantity, price, status, created_at
            from orders
            where run_id = ?
            order by id asc
            """,
            (run_id,),
        ).fetchall()
        return [dict(row) for row in rows]


class FillRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def save_fill(
        self,
        run_id: str,
        fill_id: str,
        order_id: str,
        symbol: str,
        quantity: int,
        price: float,
        filled_at: str,
    ) -> None:
        self.conn.execute(
            """
            insert into fills (run_id, fill_id, order_id, symbol, quantity, price, filled_at)
            values (?, ?, ?, ?, ?, ?, ?)
            on conflict(fill_id) do update set
                run_id = excluded.run_id,
                order_id = excluded.order_id,
                symbol = excluded.symbol,
                quantity = excluded.quantity,
                price = excluded.price,
                filled_at = excluded.filled_at
            """,
            (run_id, fill_id, order_id, symbol, quantity, price, filled_at),
        )
        self.conn.commit()

    def list_by_run(self, run_id: str) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            select id, run_id, fill_id, order_id, symbol, quantity, price, filled_at
            from fills
            where run_id = ?
            order by id asc
            """,
            (run_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    def list_by_order(self, order_id: str) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            select id, run_id, fill_id, order_id, symbol, quantity, price, filled_at
            from fills
            where order_id = ?
            order by id asc
            """,
            (order_id,),
        ).fetchall()
        return [dict(row) for row in rows]


class AccountSnapshotRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def save_snapshot(
        self,
        run_id: str,
        cash: float,
        total_asset: float,
        position_value: float,
        snapshot_at: str | None = None,
    ) -> None:
        self.conn.execute(
            """
            insert into account_snapshot (run_id, cash, total_asset, position_value, snapshot_at)
            values (?, ?, ?, ?, coalesce(?, current_timestamp))
            """,
            (run_id, cash, total_asset, position_value, snapshot_at),
        )
        self.conn.commit()

    def list_by_run(self, run_id: str) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            select id, run_id, cash, total_asset, position_value, snapshot_at
            from account_snapshot
            where run_id = ?
            order by id asc
            """,
            (run_id,),
        ).fetchall()
        return [dict(row) for row in rows]


class MemoryEntryRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def save_entry(
        self,
        run_id: str,
        memory_type: str,
        title: str,
        content: str,
        score: float,
        status: str,
        symbol: str | None = None,
    ) -> None:
        self.conn.execute(
            """
            insert into memory_entry (run_id, memory_type, symbol, title, content, score, status)
            values (?, ?, ?, ?, ?, ?, ?)
            """,
            (run_id, memory_type, symbol, title, content, score, status),
        )
        self.conn.commit()

    def list_by_run(self, run_id: str) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            select id, run_id, memory_type, symbol, title, content, score, status, created_at
            from memory_entry
            where run_id = ?
            order by id asc
            """,
            (run_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    def list_by_type(self, memory_type: str) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            select id, run_id, memory_type, symbol, title, content, score, status, created_at
            from memory_entry
            where memory_type = ?
            order by id asc
            """,
            (memory_type,),
        ).fetchall()
        return [dict(row) for row in rows]
