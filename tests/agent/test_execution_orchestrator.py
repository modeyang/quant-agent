from src.agent.orchestrator import run_p0_cycle
from src.data.runtime import build_research_runtime


def test_run_p0_cycle_execute_mode_persists_orders_fills_and_run_log(
    tmp_path,
    fake_provider,
    fake_broker,
):
    runtime = build_research_runtime(db_path=tmp_path / "quant.db", provider=fake_provider)

    result = run_p0_cycle(
        mode="manual_execute",
        runtime=runtime,
        broker=fake_broker,
        approval_granted=True,
        symbols=["600000.SH"],
        start="2026-03-01",
        end="2026-03-27",
        min_score=60.0,
    )

    run_id = result["planning"]["run_id"]
    orders = runtime.order_repo.list_by_run(run_id)
    fills = runtime.fill_repo.list_by_run(run_id)
    snapshots = runtime.account_snapshot_repo.list_by_run(run_id)
    memory_entries = runtime.memory_entry_repo.list_by_run(run_id)
    run_log = runtime.run_log_repo.get_by_run(run_id)

    assert result["execution"]["status"] == "done"
    assert result["execution"]["order_count"] == 1
    assert result["execution"]["fill_count"] == 1
    assert result["execution"]["shadow_order_count"] == 0
    assert result["review"]["status"] == "ready"
    assert result["monitoring"]["status"] == "reinforced"
    assert result["memory"]["status"] == "ready"
    assert result["memory"]["entry_count"] >= 1
    assert len(fake_broker.placed_orders) == 1
    assert len(orders) == 1
    assert orders[0]["status"] == "reconciled"
    assert len(fills) == 1
    assert len(snapshots) == 1
    assert len(memory_entries) >= 1
    assert run_log is not None
    assert run_log["status"] == "success"
    assert run_log["stage"] == "completed"


def test_run_p0_cycle_execute_mode_blocks_without_manual_approval(
    tmp_path,
    fake_provider,
    fake_broker,
):
    runtime = build_research_runtime(db_path=tmp_path / "quant.db", provider=fake_provider)

    result = run_p0_cycle(
        mode="manual_execute",
        runtime=runtime,
        broker=fake_broker,
        approval_granted=False,
        symbols=["600000.SH"],
        start="2026-03-01",
        end="2026-03-27",
        min_score=60.0,
    )

    run_id = result["planning"]["run_id"]
    orders = runtime.order_repo.list_by_run(run_id)
    fills = runtime.fill_repo.list_by_run(run_id)
    memory_entries = runtime.memory_entry_repo.list_by_run(run_id)
    run_log = runtime.run_log_repo.get_by_run(run_id)

    assert result["execution"]["status"] == "blocked"
    assert result["execution"]["order_count"] == 1
    assert result["execution"]["fill_count"] == 0
    assert result["execution"]["shadow_order_count"] == 0
    assert result["execution"]["blocked_count"] == 1
    assert result["execution"]["rejected_count"] == 1
    assert result["monitoring"]["status"] == "alert"
    assert result["memory"]["status"] == "ready"
    assert len(fake_broker.placed_orders) == 0
    assert len(orders) == 1
    assert orders[0]["status"] == "rejected"
    assert fills == []
    assert len(memory_entries) >= 1
    assert run_log is not None
    assert run_log["status"] == "success"
    assert run_log["stage"] == "completed"


def test_run_p0_cycle_execute_mode_requires_broker(tmp_path, fake_provider):
    runtime = build_research_runtime(db_path=tmp_path / "quant.db", provider=fake_provider)

    result = run_p0_cycle(
        mode="manual_execute",
        runtime=runtime,
        broker=None,
        approval_granted=True,
        symbols=["600000.SH"],
        start="2026-03-01",
        end="2026-03-27",
        min_score=60.0,
    )

    run_id = result["planning"]["run_id"]
    run_log = runtime.run_log_repo.get_by_run(run_id)

    assert result["execution"]["status"] == "unavailable"
    assert "missing broker" in result["execution"]["reason"]
    assert result["execution"]["shadow_order_count"] == 0
    assert result["review"]["status"] == "pending"
    assert result["monitoring"]["status"] == "pending"
    assert result["memory"]["status"] == "skipped"
    assert run_log is not None
    assert run_log["status"] == "failed"
    assert run_log["stage"] == "failed"


def test_run_p0_cycle_execute_mode_with_xtquant_mode_reports_config_error(tmp_path, fake_provider):
    runtime = build_research_runtime(db_path=tmp_path / "quant.db", provider=fake_provider)

    result = run_p0_cycle(
        mode="manual_execute",
        runtime=runtime,
        broker=None,
        broker_mode="xtquant",
        account_config_path=tmp_path / "missing-account.yaml",
        approval_granted=True,
        symbols=["600000.SH"],
        start="2026-03-01",
        end="2026-03-27",
        min_score=60.0,
    )

    assert result["execution"]["status"] == "unavailable"
    assert "account config not found" in result["execution"]["reason"]
    assert result["execution"]["shadow_order_count"] == 0


def test_run_p0_cycle_execute_mode_retries_and_succeeds(tmp_path, fake_provider):
    class FlakyBroker:
        def __init__(self) -> None:
            self.calls = 0

        def place_order(self, intent):
            self.calls += 1
            if self.calls == 1:
                raise RuntimeError("temporary error")
            return {"result": "ok"}

    runtime = build_research_runtime(db_path=tmp_path / "quant.db", provider=fake_provider)
    broker = FlakyBroker()

    result = run_p0_cycle(
        mode="manual_execute",
        runtime=runtime,
        broker=broker,
        max_place_retries=2,
        approval_granted=True,
        symbols=["600000.SH"],
        start="2026-03-01",
        end="2026-03-27",
        min_score=60.0,
    )

    run_id = result["planning"]["run_id"]
    orders = runtime.order_repo.list_by_run(run_id)
    fills = runtime.fill_repo.list_by_run(run_id)
    run_log = runtime.run_log_repo.get_by_run(run_id)

    assert broker.calls == 2
    assert result["execution"]["status"] == "done"
    assert result["execution"]["shadow_order_count"] == 0
    assert result["execution"]["alerts"] == []
    assert len(orders) == 1
    assert orders[0]["status"] == "reconciled"
    assert len(fills) == 1
    assert run_log is not None
    assert run_log["status"] == "success"


def test_run_p0_cycle_execute_mode_fails_after_retries_exhausted(tmp_path, fake_provider):
    class FailingBroker:
        def __init__(self) -> None:
            self.calls = 0

        def place_order(self, intent):
            self.calls += 1
            raise RuntimeError("permanent error")

    runtime = build_research_runtime(db_path=tmp_path / "quant.db", provider=fake_provider)
    broker = FailingBroker()

    result = run_p0_cycle(
        mode="manual_execute",
        runtime=runtime,
        broker=broker,
        max_place_retries=2,
        approval_granted=True,
        symbols=["600000.SH"],
        start="2026-03-01",
        end="2026-03-27",
        min_score=60.0,
    )

    run_id = result["planning"]["run_id"]
    orders = runtime.order_repo.list_by_run(run_id)
    fills = runtime.fill_repo.list_by_run(run_id)
    run_log = runtime.run_log_repo.get_by_run(run_id)

    assert broker.calls == 2
    assert result["execution"]["status"] == "failed"
    assert result["execution"]["shadow_order_count"] == 0
    assert len(result["execution"]["alerts"]) == 1
    assert result["execution"]["alerts"][0]["type"] == "place_order_failed"
    assert len(orders) == 1
    assert orders[0]["status"] == "rejected"
    assert fills == []
    assert run_log is not None
    assert run_log["status"] == "failed"
    assert run_log["stage"] == "failed"


def test_run_p0_cycle_execute_mode_shadow_without_real_broker(tmp_path, fake_provider):
    runtime = build_research_runtime(db_path=tmp_path / "quant.db", provider=fake_provider)

    result = run_p0_cycle(
        mode="manual_execute",
        runtime=runtime,
        broker=None,
        broker_mode="shadow",
        approval_granted=True,
        symbols=["600000.SH"],
        start="2026-03-01",
        end="2026-03-27",
        min_score=60.0,
    )

    run_id = result["planning"]["run_id"]
    orders = runtime.order_repo.list_by_run(run_id)
    fills = runtime.fill_repo.list_by_run(run_id)
    run_log = runtime.run_log_repo.get_by_run(run_id)

    assert result["execution"]["status"] == "shadow"
    assert result["execution"]["order_count"] == 1
    assert result["execution"]["fill_count"] == 0
    assert result["execution"]["shadow_order_count"] == 1
    assert result["execution"]["alerts"] == []
    assert orders[0]["status"] == "shadow_submitted"
    assert fills == []
    assert run_log is not None
    assert run_log["status"] == "success"
    assert run_log["stage"] == "completed"
