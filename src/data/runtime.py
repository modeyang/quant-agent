from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sqlite3

from src.data.adata_adapter import AdataAdapter
from src.data.db import connect_db
from src.data.provider_base import MarketDataProvider
from src.data.repositories import PlanRepository
from src.data.schema import init_schema


@dataclass(slots=True)
class ResearchRuntime:
    provider: MarketDataProvider
    conn: sqlite3.Connection
    plan_repo: PlanRepository
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
        db_path=path,
    )
