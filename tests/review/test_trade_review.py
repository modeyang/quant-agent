from src.review.trade_review import build_trade_review


def test_build_trade_review_summarizes_plan_vs_actual():
    review = build_trade_review(trade_date="2026-03-27", planned=2, executed=1, rejected=1)

    assert review.executed_count == 1
    assert review.rejected_count == 1


def test_build_trade_review_adds_gap_note_when_execution_misses_plan():
    review = build_trade_review(trade_date="2026-03-27", planned=3, executed=1, rejected=0)

    assert any("plan gap" in note for note in review.notes)
