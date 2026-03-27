from src.common.models import CandidatePlan
from src.data.db import connect_db
from src.data.repositories import PlanRepository
from src.data.schema import init_schema


def test_plan_repository_round_trip(tmp_path):
    conn = connect_db(tmp_path / "quant.db")
    init_schema(conn)
    repo = PlanRepository(conn)

    repo.save_plan("run-1", "600000.SH", "stock", 85.0)
    saved = repo.list_by_run("run-1")

    assert saved[0]["symbol"] == "600000.SH"
    assert saved[0]["score"] == 85.0


def test_plan_repository_upserts_duplicate_run_and_symbol(tmp_path):
    conn = connect_db(tmp_path / "quant.db")
    init_schema(conn)
    repo = PlanRepository(conn)

    repo.save_plan("run-1", "600000.SH", "stock", 85.0)
    repo.save_plan("run-1", "600000.SH", "stock", 90.0)
    saved = repo.list_by_run("run-1")

    assert len(saved) == 1
    assert saved[0]["score"] == 90.0


def test_plan_repository_saves_bulk_plans(tmp_path):
    conn = connect_db(tmp_path / "quant.db")
    init_schema(conn)
    repo = PlanRepository(conn)

    repo.save_candidate_plans(
        "run-1",
        [
            CandidatePlan(symbol="600000.SH", asset_type="stock", score=80.0),
            CandidatePlan(symbol="510300.SH", asset_type="etf", score=78.0),
        ],
    )
    saved = repo.list_by_run("run-1")

    assert len(saved) == 2
