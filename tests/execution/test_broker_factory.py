from src.execution.broker_factory import resolve_execution_broker


def test_resolve_execution_broker_prefers_explicit_broker():
    explicit = object()
    broker, error = resolve_execution_broker(
        explicit_broker=explicit,
        broker_mode="xtquant",
        account_config_path="config/account.yaml",
    )

    assert broker is explicit
    assert error is None


def test_resolve_execution_broker_reports_missing_when_injected_mode():
    broker, error = resolve_execution_broker(
        explicit_broker=None,
        broker_mode="injected",
        account_config_path="config/account.yaml",
    )

    assert broker is None
    assert error == "missing broker for execute mode"


def test_resolve_execution_broker_reports_missing_account_config_for_xtquant(tmp_path):
    broker, error = resolve_execution_broker(
        explicit_broker=None,
        broker_mode="xtquant",
        account_config_path=tmp_path / "missing-account.yaml",
    )

    assert broker is None
    assert error is not None
    assert "account config not found" in error


def test_resolve_execution_broker_returns_shadow_broker():
    broker, error = resolve_execution_broker(
        explicit_broker=None,
        broker_mode="shadow",
        account_config_path="config/account.yaml",
    )

    assert broker is not None
    assert getattr(broker, "mode", None) == "shadow"
    assert error is None


def test_resolve_execution_broker_supports_shadow_auto_fill_config():
    broker, error = resolve_execution_broker(
        explicit_broker=None,
        broker_mode="shadow",
        account_config_path="config/account.yaml",
        shadow_auto_fill=True,
        shadow_fill_at="2026-03-28 09:35:00",
    )

    assert broker is not None
    assert getattr(broker, "mode", None) == "shadow"
    response = broker.place_order(
        {"symbol": "600000.SH", "quantity": 100, "price": 10.5, "client_order_id": "run-1-O001"}
    )
    assert response["shadow_fill_id"] == "run-1-O001-F001"
    assert broker.query_fills()[0]["filled_at"] == "2026-03-28 09:35:00"
    assert error is None
