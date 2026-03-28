from src.monitoring.intraday_watch import assess_intraday_watch


def test_assess_intraday_watch_marks_reinforced_when_filled():
    result = assess_intraday_watch(
        plans=[{"symbol": "600000.SH"}],
        orders=[{"symbol": "600000.SH"}],
        fills=[{"symbol": "600000.SH"}],
    )

    assert result["status"] == "reinforced"
    assert result["reinforced_symbols"] == ["600000.SH"]
    assert result["invalidated_symbols"] == []


def test_assess_intraday_watch_marks_alert_when_not_ordered():
    result = assess_intraday_watch(
        plans=[{"symbol": "600000.SH"}, {"symbol": "510300.SH"}],
        orders=[{"symbol": "600000.SH"}],
        fills=[],
    )

    assert result["status"] == "alert"
    assert result["invalidated_symbols"] == ["510300.SH"]


def test_assess_intraday_watch_treats_rejected_orders_as_invalidated():
    result = assess_intraday_watch(
        plans=[{"symbol": "600000.SH"}],
        orders=[{"symbol": "600000.SH", "status": "rejected"}],
        fills=[],
    )

    assert result["status"] == "alert"
    assert result["invalidated_symbols"] == ["600000.SH"]
