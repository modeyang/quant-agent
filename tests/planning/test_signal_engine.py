from src.planning.signal_engine import score_candidate


def test_score_candidate_combines_event_trend_and_fund_flow():
    score = score_candidate(
        event_score=80,
        trend_score=70,
        flow_score=90,
        weights={"event": 0.4, "trend": 0.3, "flow": 0.3},
    )

    assert score == 80.0
