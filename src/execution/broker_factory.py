from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from src.execution.broker_shadow import ShadowBroker
from src.execution.broker_xtquant import XtquantBroker


def _load_account_config(path: str | Path) -> dict[str, Any]:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"account config not found: {config_path}")
    with config_path.open("r", encoding="utf-8") as file:
        raw = yaml.safe_load(file) or {}
    return raw


def build_xtquant_broker(account_config_path: str | Path) -> tuple[Any | None, str | None]:
    try:
        config = _load_account_config(account_config_path)
    except Exception as exc:
        return None, str(exc)

    try:
        from xtquant import xttrader, xttype  # type: ignore
    except Exception as exc:
        return None, f"xtquant import failed: {exc}"

    try:
        qmt_path = config["connection"]["qmt_path"]
        session_id = int(config["connection"]["session_id"])
        account_id = config["account"]["account_id"]
    except Exception as exc:
        return None, f"invalid account config: {exc}"

    try:
        trader_client = xttrader.XtQuantTrader(qmt_path, session_id)
        stock_account = xttype.StockAccount(account_id)
        return XtquantBroker(trader_client=trader_client, account=stock_account), None
    except Exception as exc:
        return None, f"xtquant broker init failed: {exc}"


def resolve_execution_broker(
    explicit_broker: Any | None,
    broker_mode: str,
    account_config_path: str | Path,
) -> tuple[Any | None, str | None]:
    if explicit_broker is not None:
        return explicit_broker, None

    if broker_mode == "xtquant":
        return build_xtquant_broker(account_config_path=account_config_path)

    if broker_mode == "shadow":
        return ShadowBroker(), None

    return None, "missing broker for execute mode"
