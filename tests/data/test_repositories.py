from src.common.models import CandidatePlan
from src.data.db import connect_db
from src.data.repositories import (
    AccountSnapshotRepository,
    FillRepository,
    MemoryEntryRepository,
    OrderRepository,
    PlanRepository,
    RunLogRepository,
    RunStageEventRepository,
)
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


def test_run_log_repository_start_and_finish_run(tmp_path):
    conn = connect_db(tmp_path / "quant.db")
    init_schema(conn)
    repo = RunLogRepository(conn)

    repo.start_run("run-1", mode="plan_only", stage="planning", message="started")
    repo.advance_stage("run-1", stage="execution", message="executing")
    repo.finish_run("run-1", status="success", stage="completed", message="completed")
    saved = repo.get_by_run("run-1")

    assert saved is not None
    assert saved["status"] == "success"
    assert saved["mode"] == "plan_only"
    assert saved["stage"] == "completed"
    assert saved["finished_at"] is not None


def test_order_repository_upserts_and_updates_status(tmp_path):
    conn = connect_db(tmp_path / "quant.db")
    init_schema(conn)
    repo = OrderRepository(conn)

    repo.save_order(
        run_id="run-1",
        order_id="order-1",
        symbol="600000.SH",
        side="buy",
        quantity=100,
        price=10.5,
        status="submitted",
    )
    repo.update_status(order_id="order-1", status="filled")
    saved = repo.list_by_run("run-1")

    assert len(saved) == 1
    assert saved[0]["order_id"] == "order-1"
    assert saved[0]["status"] == "filled"


def test_fill_repository_round_trip(tmp_path):
    conn = connect_db(tmp_path / "quant.db")
    init_schema(conn)
    repo = FillRepository(conn)

    repo.save_fill(
        run_id="run-1",
        fill_id="fill-1",
        order_id="order-1",
        symbol="600000.SH",
        quantity=100,
        price=10.45,
        filled_at="2026-03-27 14:50:00",
    )
    by_run = repo.list_by_run("run-1")
    by_order = repo.list_by_order("order-1")

    assert len(by_run) == 1
    assert by_run[0]["fill_id"] == "fill-1"
    assert len(by_order) == 1
    assert by_order[0]["price"] == 10.45


def test_account_snapshot_repository_round_trip(tmp_path):
    conn = connect_db(tmp_path / "quant.db")
    init_schema(conn)
    repo = AccountSnapshotRepository(conn)

    repo.save_snapshot(
        run_id="run-1",
        cash=100000.0,
        total_asset=150000.0,
        position_value=50000.0,
        snapshot_at="2026-03-27 15:00:00",
    )
    saved = repo.list_by_run("run-1")

    assert len(saved) == 1
    assert saved[0]["cash"] == 100000.0
    assert saved[0]["total_asset"] == 150000.0


def test_memory_entry_repository_round_trip(tmp_path):
    conn = connect_db(tmp_path / "quant.db")
    init_schema(conn)
    repo = MemoryEntryRepository(conn)

    repo.save_entry(
        run_id="run-1",
        memory_type="trade_memory",
        symbol="600000.SH",
        title="trade review",
        content="planned=1, executed=1, rejected=0",
        score=0.9,
        status="confirmed",
    )
    by_run = repo.list_by_run("run-1")
    by_type = repo.list_by_type("trade_memory")

    assert len(by_run) == 1
    assert by_run[0]["symbol"] == "600000.SH"
    assert by_run[0]["status"] == "confirmed"
    assert len(by_type) == 1


def test_run_stage_event_repository_round_trip(tmp_path):
    conn = connect_db(tmp_path / "quant.db")
    init_schema(conn)
    repo = RunStageEventRepository(conn)

    repo.append_event(run_id="run-1", stage="planning", status="running", message="start")
    repo.append_event(run_id="run-1", stage="execution", status="running", message="orders")
    events = repo.list_by_run("run-1")

    assert len(events) == 2
    assert events[0]["stage"] == "planning"
    assert events[1]["stage"] == "execution"
