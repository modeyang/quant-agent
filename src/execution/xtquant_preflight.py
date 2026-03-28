from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import Any

import yaml


CheckResult = dict[str, str]
PreflightResult = dict[str, Any]


_REQUIRED_PATHS: tuple[tuple[str, ...], ...] = (
    ("connection", "qmt_path"),
    ("connection", "session_id"),
    ("account", "account_id"),
)


def _read_yaml_config(config_path: Path) -> tuple[dict[str, Any], str | None]:
    if not config_path.exists():
        return {}, f"account config not found: {config_path}"

    try:
        with config_path.open("r", encoding="utf-8") as file:
            loaded = yaml.safe_load(file)
    except Exception as exc:
        return {}, f"account config parse failed: {exc}"

    if loaded is None:
        return {}, None
    if not isinstance(loaded, dict):
        return {}, "account config must be a YAML mapping"
    return loaded, None


def _missing_required_keys(config: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    for path in _REQUIRED_PATHS:
        cursor: Any = config
        found = True
        for key in path:
            if not isinstance(cursor, dict) or key not in cursor:
                found = False
                break
            cursor = cursor[key]

        if not found or cursor in (None, ""):
            missing.append(".".join(path))
    return missing


def _check_xtquant_importable() -> str | None:
    try:
        import_module("xtquant")
    except Exception as exc:
        return f"xtquant import failed: {exc}"
    return None


def run_xtquant_preflight(account_config_path: str | Path) -> PreflightResult:
    """Run deterministic local checks before xtquant real-broker execution."""
    config_path = Path(account_config_path)
    checks: list[CheckResult] = []

    config, config_error = _read_yaml_config(config_path)
    if config_error is None:
        checks.append(
            {
                "name": "account_config",
                "status": "pass",
                "message": f"account config loaded: {config_path}",
            }
        )
    else:
        checks.append(
            {
                "name": "account_config",
                "status": "fail",
                "message": config_error,
            }
        )

    missing_keys = _missing_required_keys(config) if config_error is None else list(
        ".".join(path) for path in _REQUIRED_PATHS
    )
    if not missing_keys:
        checks.append(
            {
                "name": "required_keys",
                "status": "pass",
                "message": "required account keys are present",
            }
        )
    else:
        checks.append(
            {
                "name": "required_keys",
                "status": "fail",
                "message": f"missing required keys: {', '.join(missing_keys)}",
            }
        )

    import_error = _check_xtquant_importable()
    if import_error is None:
        checks.append(
            {
                "name": "xtquant_import",
                "status": "pass",
                "message": "xtquant module import is available",
            }
        )
    else:
        checks.append(
            {
                "name": "xtquant_import",
                "status": "fail",
                "message": import_error,
            }
        )

    failed_checks = [check for check in checks if check["status"] == "fail"]
    if not failed_checks:
        return {
            "status": "ok",
            "checks": checks,
            "message": "xtquant preflight passed: local config and import checks are ready.",
        }

    return {
        "status": "error",
        "checks": checks,
        "message": "xtquant preflight failed: fix failed checks before real-broker execution.",
    }
