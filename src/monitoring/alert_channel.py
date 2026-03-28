from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

_SUPPORTED_CHANNELS = {"stdout", "file"}

_DEFAULT_ALERT_CONFIG: dict[str, Any] = {
    "enabled": True,
    "channels": ["stdout"],
    "file_path": "data/logs/alerts.jsonl",
}


def normalize_alert_config(raw: dict[str, Any] | None) -> dict[str, Any]:
    """Normalize alert config into a safe runtime shape."""
    if not isinstance(raw, dict):
        return dict(_DEFAULT_ALERT_CONFIG)

    enabled = bool(raw.get("enabled", _DEFAULT_ALERT_CONFIG["enabled"]))

    channels_raw = raw.get("channels", _DEFAULT_ALERT_CONFIG["channels"])
    channels: list[str]
    if isinstance(channels_raw, str):
        channels = [channels_raw]
    elif isinstance(channels_raw, list):
        channels = [str(item) for item in channels_raw]
    else:
        channels = list(_DEFAULT_ALERT_CONFIG["channels"])

    normalized_channels: list[str] = []
    for channel in channels:
        lowered = channel.strip().lower()
        if lowered in _SUPPORTED_CHANNELS and lowered not in normalized_channels:
            normalized_channels.append(lowered)
    if not normalized_channels:
        normalized_channels = list(_DEFAULT_ALERT_CONFIG["channels"])

    file_path = str(raw.get("file_path", _DEFAULT_ALERT_CONFIG["file_path"]))

    return {
        "enabled": enabled,
        "channels": normalized_channels,
        "file_path": file_path,
    }


def _build_envelopes(
    run_id: str,
    alerts: list[dict[str, Any]],
    emitted_at: str,
) -> list[dict[str, Any]]:
    return [
        {
            "run_id": run_id,
            "emitted_at": emitted_at,
            "alert": dict(alert),
        }
        for alert in alerts
    ]


def _dispatch_stdout(envelopes: list[dict[str, Any]]) -> None:
    for item in envelopes:
        print(json.dumps(item, ensure_ascii=False, sort_keys=True))


def _dispatch_file(envelopes: list[dict[str, Any]], file_path: str) -> None:
    target = Path(file_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as file:
        for item in envelopes:
            file.write(json.dumps(item, ensure_ascii=False, sort_keys=True))
            file.write("\n")


def dispatch_alerts(
    run_id: str,
    alerts: list[dict[str, Any]] | None,
    config: dict[str, Any] | None = None,
    emitted_at: str | None = None,
) -> dict[str, Any]:
    """Dispatch alerts to configured channels and capture channel-level failures."""
    normalized = normalize_alert_config(config)
    if not normalized["enabled"]:
        return {
            "enabled": False,
            "alerts_count": 0,
            "ok": True,
            "failed_channels": [],
            "channels": [],
            "status": "disabled",
        }

    sanitized_alerts = [item for item in (alerts or []) if isinstance(item, dict)]
    if not sanitized_alerts:
        return {
            "enabled": True,
            "alerts_count": 0,
            "ok": True,
            "failed_channels": [],
            "channels": [],
            "status": "no_alerts",
        }

    ts = emitted_at or datetime.now().isoformat(timespec="seconds")
    envelopes = _build_envelopes(run_id=run_id, alerts=sanitized_alerts, emitted_at=ts)

    channel_results: list[dict[str, Any]] = []
    for channel in normalized["channels"]:
        try:
            if channel == "stdout":
                _dispatch_stdout(envelopes)
            elif channel == "file":
                _dispatch_file(envelopes, file_path=normalized["file_path"])
            else:
                raise ValueError(f"unsupported alert channel: {channel}")
            channel_results.append(
                {
                    "channel": channel,
                    "ok": True,
                    "delivered_count": len(envelopes),
                    "error": None,
                }
            )
        except Exception as exc:
            channel_results.append(
                {
                    "channel": channel,
                    "ok": False,
                    "delivered_count": 0,
                    "error": str(exc),
                }
            )

    failed_channels = [item["channel"] for item in channel_results if not item["ok"]]
    return {
        "enabled": True,
        "alerts_count": len(envelopes),
        "ok": len(failed_channels) == 0,
        "failed_channels": failed_channels,
        "channels": channel_results,
        "status": "delivered" if not failed_channels else "partial_failure",
    }
