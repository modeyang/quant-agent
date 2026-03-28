from __future__ import annotations

from typing import Any


class ShadowBroker:
    mode = "shadow"

    def __init__(self) -> None:
        self._orders: list[dict[str, Any]] = []

    def place_order(self, intent: dict[str, Any]) -> dict[str, Any]:
        order = dict(intent)
        self._orders.append(order)
        return {
            "result": "shadow_accepted",
            "shadow_order_id": f"shadow-{len(self._orders):04d}",
        }

    def cancel_order(self, order_id: str) -> dict[str, Any]:
        return {"result": "shadow_cancelled", "order_id": order_id}

    def query_orders(self) -> list[dict[str, Any]]:
        return [dict(item) for item in self._orders]

