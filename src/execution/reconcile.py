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
