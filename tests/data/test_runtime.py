from src.data.runtime import build_research_runtime


def test_build_research_runtime_returns_db_and_provider(tmp_path, fake_provider):
    runtime = build_research_runtime(db_path=tmp_path / "quant.db", provider=fake_provider)

    assert runtime.provider is fake_provider
    assert runtime.plan_repo is not None
    assert runtime.run_log_repo is not None
    assert runtime.run_stage_event_repo is not None
    assert runtime.order_repo is not None
    assert runtime.fill_repo is not None
    assert runtime.account_snapshot_repo is not None
    assert runtime.memory_entry_repo is not None
    assert (tmp_path / "quant.db").exists()
