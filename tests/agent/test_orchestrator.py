from src.agent.orchestrator import run_p0_cycle


def test_run_p0_cycle_returns_plan_execute_review_sections():
    result = run_p0_cycle(mode="plan_only")

    assert {"planning", "execution", "review"}.issubset(result.keys())
    assert result["execution"]["status"] == "skipped"
