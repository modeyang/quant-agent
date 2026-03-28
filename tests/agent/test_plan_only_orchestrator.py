from src.agent.orchestrator import run_p0_cycle
from src.data.runtime import build_research_runtime


def test_run_p0_cycle_plan_only_persists_ranked_plans(tmp_path, fake_provider):
    runtime = build_research_runtime(db_path=tmp_path / "quant.db", provider=fake_provider)

    result = run_p0_cycle(
        mode="plan_only",
        runtime=runtime,
        symbols=["600000.SH"],
        start="2026-03-01",
        end="2026-03-27",
        min_score=60.0,
    )

    assert result["planning"]["status"] == "ready"
    assert result["planning"]["plan_count"] == 1
    assert result["planning"]["plans"][0]["symbol"] == "600000.SH"
    assert result["run"]["status"] == "success"
    assert result["run"]["stage"] == "completed"
    assert result["monitoring"]["status"] == "pending"
    assert result["memory"]["status"] == "skipped"
    assert result["memory"]["entry_count"] == 0

    saved = runtime.plan_repo.list_by_run(result["planning"]["run_id"])
    assert len(saved) == 1


def test_run_p0_cycle_plan_only_allows_empty_plan_set(tmp_path, fake_provider):
    runtime = build_research_runtime(db_path=tmp_path / "quant.db", provider=fake_provider)

    result = run_p0_cycle(
        mode="plan_only",
        runtime=runtime,
        symbols=["600000.SH"],
        start="2026-03-01",
        end="2026-03-27",
        min_score=95.0,
    )

    assert result["planning"]["plan_count"] == 0
    assert result["planning"]["plans"] == []
    assert result["memory"]["entry_count"] == 0
    assert "stage_events" in result["execution"]
    assert result["execution"]["stage_duration_seconds"]["planning"] >= 0.0
    assert "completed" in result["execution"]["stage_duration_seconds"]
    assert "planning=" in result["review"]["stage_timing_summary"]
