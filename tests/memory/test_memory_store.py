from src.memory.conflict_resolver import resolve_memory_conflicts
from src.memory.memory_store import build_trade_memory_entries


def test_build_trade_memory_entries_for_ready_review_and_monitoring():
    entries = build_trade_memory_entries(
        run_id="run-1",
        review_payload={
            "status": "ready",
            "trade_date": "2026-03-27",
            "planned_count": 2,
            "executed_count": 2,
            "rejected_count": 0,
            "notes": [],
        },
        monitoring_payload={
            "status": "reinforced",
            "invalidated_symbols": [],
            "reinforced_symbols": ["600000.SH"],
        },
    )

    assert len(entries) == 2
    assert {item["memory_type"] for item in entries} == {"trade_memory", "market_memory"}


def test_resolve_memory_conflicts_keeps_higher_score():
    deduped = resolve_memory_conflicts(
        [
            {
                "memory_type": "trade_memory",
                "title": "trade review 2026-03-27",
                "symbol": None,
                "score": 0.7,
            },
            {
                "memory_type": "trade_memory",
                "title": "trade review 2026-03-27",
                "symbol": None,
                "score": 0.9,
            },
        ]
    )

    assert len(deduped) == 1
    assert deduped[0]["score"] == 0.9

