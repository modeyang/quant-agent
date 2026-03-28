from __future__ import annotations

from typing import Any


def reconcile_run(orders: list[dict[str, Any]], fills: list[dict[str, Any]]) -> dict[str, Any]:
    filled_ids = {fill["order_id"] for fill in fills}
    reconciled = 0
    unmatched_order_ids: list[str] = []

    for order in orders:
        if order["order_id"] in filled_ids:
            reconciled += 1
        else:
            unmatched_order_ids.append(order["order_id"])

    return {
        "reconciled": reconciled,
        "unmatched_order_ids": unmatched_order_ids,
    }


def _extract_order_id(item: dict[str, Any]) -> str | None:
    for key in ("order_id", "client_order_id"):
        value = item.get(key)
        if value is not None and str(value) != "":
            return str(value)
    return None


def reconcile_with_broker_snapshot(
    local_orders: list[dict[str, Any]],
    local_fills: list[dict[str, Any]],
    broker_orders: list[dict[str, Any]],
    broker_fills: list[dict[str, Any]],
) -> dict[str, Any]:
    local_summary = reconcile_run(local_orders, local_fills)
    local_order_ids = {item["order_id"] for item in local_orders}
    local_fill_order_ids = {item["order_id"] for item in local_fills}
    broker_order_ids = {oid for oid in (_extract_order_id(item) for item in broker_orders) if oid}
    broker_fill_order_ids = {oid for oid in (_extract_order_id(item) for item in broker_fills) if oid}

    missing_on_broker_order_ids = sorted(local_order_ids - broker_order_ids)
    extra_on_broker_order_ids = sorted(broker_order_ids - local_order_ids)
    missing_on_broker_fill_order_ids = sorted(local_fill_order_ids - broker_fill_order_ids)
    extra_on_broker_fill_order_ids = sorted(broker_fill_order_ids - local_fill_order_ids)

    strict_ok = (
        not missing_on_broker_order_ids
        and not extra_on_broker_order_ids
        and not missing_on_broker_fill_order_ids
        and not extra_on_broker_fill_order_ids
    )
    return {
        **local_summary,
        "missing_on_broker_order_ids": missing_on_broker_order_ids,
        "extra_on_broker_order_ids": extra_on_broker_order_ids,
        "missing_on_broker_fill_order_ids": missing_on_broker_fill_order_ids,
        "extra_on_broker_fill_order_ids": extra_on_broker_fill_order_ids,
        "strict_ok": strict_ok,
    }
