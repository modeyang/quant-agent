from src.execution.reconcile import reconcile_run


def test_reconcile_run_marks_filled_order_as_reconciled():
    result = reconcile_run(
        orders=[{"order_id": "o1", "status": "filled"}],
        fills=[{"order_id": "o1", "qty": 100}],
    )

    assert result["reconciled"] == 1


def test_reconcile_run_reports_unmatched_orders():
    result = reconcile_run(
        orders=[{"order_id": "o1", "status": "filled"}, {"order_id": "o2", "status": "submitted"}],
        fills=[{"order_id": "o1", "qty": 100}],
    )

    assert result["unmatched_order_ids"] == ["o2"]
