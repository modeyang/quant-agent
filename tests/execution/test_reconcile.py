from src.execution.reconcile import reconcile_run, reconcile_with_broker_snapshot


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


def test_reconcile_with_broker_snapshot_is_strict_when_ids_match():
    result = reconcile_with_broker_snapshot(
        local_orders=[{"order_id": "o1"}, {"order_id": "o2"}],
        local_fills=[{"order_id": "o1"}],
        broker_orders=[{"order_id": "o1"}, {"client_order_id": "o2"}],
        broker_fills=[{"order_id": "o1"}],
    )

    assert result["strict_ok"] is True
    assert result["missing_on_broker_order_ids"] == []
    assert result["extra_on_broker_order_ids"] == []
    assert result["missing_on_broker_fill_order_ids"] == []
    assert result["extra_on_broker_fill_order_ids"] == []


def test_reconcile_with_broker_snapshot_reports_mismatch_details():
    result = reconcile_with_broker_snapshot(
        local_orders=[{"order_id": "o1"}],
        local_fills=[{"order_id": "o1"}],
        broker_orders=[{"order_id": "oX"}],
        broker_fills=[],
    )

    assert result["strict_ok"] is False
    assert result["missing_on_broker_order_ids"] == ["o1"]
    assert result["extra_on_broker_order_ids"] == ["oX"]
    assert result["missing_on_broker_fill_order_ids"] == ["o1"]
