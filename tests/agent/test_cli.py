from __future__ import annotations

import json

from src.agent import cli


def test_build_parser_run_defaults():
    parser = cli.build_parser()
    args = parser.parse_args(["run"])

    assert args.command == "run"
    assert args.mode == "plan_only"
    assert args.symbols is None
    assert args.broker_mode == "shadow"
    assert args.approval_granted is False
    assert args.strict_reconcile is True
    assert args.kill_switch is True
    assert args.output == "json"


def test_run_command_parses_symbols_and_invokes_orchestrator(monkeypatch, capsys):
    captured: dict[str, object] = {}
    fake_result = {"planning": {"status": "ready"}, "execution": {"status": "done"}}

    def fake_run_p0_cycle(**kwargs):
        captured.update(kwargs)
        return fake_result

    monkeypatch.setattr(cli, "run_p0_cycle", fake_run_p0_cycle)

    exit_code = cli.main(
        [
            "run",
            "--mode",
            "manual_execute",
            "--symbols",
            "600000.SH, 000001.SZ",
            "--broker-mode",
            "xtquant",
            "--approval-granted",
            "--strict-reconcile",
            "--no-kill-switch",
        ]
    )

    assert exit_code == 0
    assert captured == {
        "mode": "manual_execute",
        "symbols": ["600000.SH", "000001.SZ"],
        "broker_mode": "xtquant",
        "approval_granted": True,
        "strict_reconcile": True,
        "kill_switch": False,
    }
    assert json.loads(capsys.readouterr().out) == fake_result


def test_run_command_returns_nonzero_for_failed_execution(monkeypatch, capsys):
    def fake_run_p0_cycle(**kwargs):
        return {"planning": {"status": "ready"}, "execution": {"status": "failed"}}

    monkeypatch.setattr(cli, "run_p0_cycle", fake_run_p0_cycle)

    exit_code = cli.main(["run", "--mode", "manual_execute"])

    assert exit_code == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["execution"]["status"] == "failed"


def test_cron_template_prints_plan_and_execute_lines(capsys):
    workspace = "/tmp/quant-agent-workspace"

    exit_code = cli.main(["cron-template", "--workspace", workspace])

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "plan_only" in output
    assert "manual_execute" in output
    assert "--approval-granted" in output
    assert "--no-kill-switch" in output
    assert workspace in output
