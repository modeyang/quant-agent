from src.planning.plan_generator import generate_plan


def test_generate_plan_returns_ranked_candidates():
    plans = generate_plan(
        run_id="run-1",
        candidates=[
            {"symbol": "600000.SH", "asset_type": "stock", "score": 82.0},
            {"symbol": "510300.SH", "asset_type": "etf", "score": 75.0},
        ],
    )

    assert plans[0].symbol == "600000.SH"
    assert plans[1].symbol == "510300.SH"


def test_generate_plan_filters_candidates_below_min_score():
    plans = generate_plan(
        run_id="run-1",
        candidates=[
            {"symbol": "600000.SH", "asset_type": "stock", "score": 82.0},
            {"symbol": "510300.SH", "asset_type": "etf", "score": 55.0},
        ],
        min_score=60.0,
    )

    assert len(plans) == 1
    assert plans[0].symbol == "600000.SH"
