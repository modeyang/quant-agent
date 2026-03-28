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

