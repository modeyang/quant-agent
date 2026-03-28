from __future__ import annotations

from src.execution.xtquant_preflight import run_xtquant_preflight


def test_run_xtquant_preflight_happy_path(tmp_path, monkeypatch):
    config_path = tmp_path / "account.yaml"
    config_path.write_text(
        "\n".join(
            [
                "connection:",
                "  qmt_path: /tmp/qmt",
                "  session_id: 1001",
                "account:",
                "  account_id: 123456",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "src.execution.xtquant_preflight.import_module",
        lambda _: object(),
    )

    result = run_xtquant_preflight(config_path)

    assert result["status"] == "ok"
    assert result["message"].startswith("xtquant preflight passed")
    assert [check["status"] for check in result["checks"]] == ["pass", "pass", "pass"]


def test_run_xtquant_preflight_reports_missing_config(monkeypatch, tmp_path):
    missing_path = tmp_path / "missing-account.yaml"

    monkeypatch.setattr(
        "src.execution.xtquant_preflight.import_module",
        lambda _: object(),
    )

    result = run_xtquant_preflight(missing_path)

    assert result["status"] == "error"
    assert result["checks"][0]["name"] == "account_config"
    assert "account config not found" in result["checks"][0]["message"]
    assert result["checks"][1]["status"] == "fail"
    assert "connection.qmt_path" in result["checks"][1]["message"]


def test_run_xtquant_preflight_reports_missing_required_keys(tmp_path, monkeypatch):
    config_path = tmp_path / "account.yaml"
    config_path.write_text(
        "\n".join(
            [
                "connection:",
                "  qmt_path: /tmp/qmt",
                "account:",
                "  account_id: 123456",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "src.execution.xtquant_preflight.import_module",
        lambda _: object(),
    )

    result = run_xtquant_preflight(config_path)

    assert result["status"] == "error"
    assert result["checks"][0]["status"] == "pass"
    assert result["checks"][1]["status"] == "fail"
    assert "connection.session_id" in result["checks"][1]["message"]


def test_run_xtquant_preflight_reports_import_failure(tmp_path, monkeypatch):
    config_path = tmp_path / "account.yaml"
    config_path.write_text(
        "\n".join(
            [
                "connection:",
                "  qmt_path: /tmp/qmt",
                "  session_id: 1001",
                "account:",
                "  account_id: 123456",
            ]
        ),
        encoding="utf-8",
    )

    def _raise(_: str) -> object:
        raise ModuleNotFoundError("No module named 'xtquant'")

    monkeypatch.setattr("src.execution.xtquant_preflight.import_module", _raise)

    result = run_xtquant_preflight(config_path)

    assert result["status"] == "error"
    assert result["checks"][0]["status"] == "pass"
    assert result["checks"][1]["status"] == "pass"
    assert result["checks"][2]["status"] == "fail"
    assert "xtquant import failed" in result["checks"][2]["message"]
