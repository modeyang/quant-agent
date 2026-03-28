from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sqlite3

from src.data.adata_adapter import AdataAdapter
from src.data.db import connect_db
from src.data.provider_base import MarketDataProvider
from src.data.repositories import (
    AccountSnapshotRepository,
    FillRepository,
    MemoryEntryRepository,
    OrderRepository,
    PlanRepository,
    RunLogRepository,
)
from src.data.schema import init_schema


@dataclass(slots=True)
class ResearchRuntime:
    provider: MarketDataProvider
    conn: sqlite3.Connection
    plan_repo: PlanRepository
    run_log_repo: RunLogRepository
    order_repo: OrderRepository
    fill_repo: FillRepository
    account_snapshot_repo: AccountSnapshotRepository
    memory_entry_repo: MemoryEntryRepository
    db_path: Path


def build_research_runtime(
    db_path: str | Path,
    provider: MarketDataProvider | None = None,
) -> ResearchRuntime:
    path = Path(db_path)
    runtime_provider = provider
    if runtime_provider is None:
        import adata  # type: ignore

        runtime_provider = AdataAdapter(adata)

    conn = connect_db(path)
    init_schema(conn)

    return ResearchRuntime(
        provider=runtime_provider,
        conn=conn,
        plan_repo=PlanRepository(conn),
        run_log_repo=RunLogRepository(conn),
        order_repo=OrderRepository(conn),
        fill_repo=FillRepository(conn),
        account_snapshot_repo=AccountSnapshotRepository(conn),
        memory_entry_repo=MemoryEntryRepository(conn),
        db_path=path,
    )
