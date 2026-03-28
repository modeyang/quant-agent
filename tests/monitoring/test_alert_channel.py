import json

from src.monitoring.alert_channel import dispatch_alerts


def test_dispatch_alerts_stdout_outputs_json_lines(capsys):
    result = dispatch_alerts(
        run_id="RUN-001",
        alerts=[
            {"type": "place_order_failed", "order_id": "O-001"},
            {"type": "reconcile_mismatch", "order_id": "O-002"},
        ],
        config={"enabled": True, "channels": ["stdout"], "file_path": "ignored.jsonl"},
        emitted_at="2026-03-28T10:00:00",
    )

    lines = [line for line in capsys.readouterr().out.splitlines() if line.strip()]
    assert len(lines) == 2
    payload_1 = json.loads(lines[0])
    payload_2 = json.loads(lines[1])
    assert payload_1["run_id"] == "RUN-001"
    assert payload_1["emitted_at"] == "2026-03-28T10:00:00"
    assert payload_1["alert"]["type"] == "place_order_failed"
    assert payload_2["alert"]["type"] == "reconcile_mismatch"

    assert result["status"] == "delivered"
    assert result["ok"] is True
    assert result["channels"][0]["channel"] == "stdout"
    assert result["channels"][0]["delivered_count"] == 2


def test_dispatch_alerts_file_appends_json_lines(tmp_path):
    file_path = tmp_path / "alerts.jsonl"
    config = {
        "enabled": True,
        "channels": ["file"],
        "file_path": str(file_path),
    }

    dispatch_alerts(
        run_id="RUN-002",
        alerts=[{"type": "connection_failure", "message": "missing broker"}],
        config=config,
        emitted_at="2026-03-28T10:01:00",
    )
    result = dispatch_alerts(
        run_id="RUN-003",
        alerts=[{"type": "connection_failure", "message": "xtquant init failed"}],
        config=config,
        emitted_at="2026-03-28T10:02:00",
    )

    lines = file_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    first = json.loads(lines[0])
    second = json.loads(lines[1])
    assert first["run_id"] == "RUN-002"
    assert second["run_id"] == "RUN-003"
    assert second["alert"]["message"] == "xtquant init failed"

    assert result["status"] == "delivered"
    assert result["channels"][0]["channel"] == "file"
    assert result["channels"][0]["delivered_count"] == 1


def test_dispatch_alerts_captures_file_channel_failure(tmp_path):
    file_path = tmp_path / "alerts-as-dir"
    file_path.mkdir()

    result = dispatch_alerts(
        run_id="RUN-004",
        alerts=[{"type": "connection_failure", "message": "broker unavailable"}],
        config={"enabled": True, "channels": ["file"], "file_path": str(file_path)},
        emitted_at="2026-03-28T10:03:00",
    )

    assert result["status"] == "partial_failure"
    assert result["ok"] is False
    assert result["failed_channels"] == ["file"]
    assert result["channels"][0]["error"]
