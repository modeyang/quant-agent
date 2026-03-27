from src.common.models import CandidatePlan


def test_candidate_plan_defaults_to_planned():
    plan = CandidatePlan(symbol="600000.SH", asset_type="stock", score=80.0)

    assert plan.status == "planned"
    assert plan.score == 80.0
