from __future__ import annotations

from typing import Any


class ShadowBroker:
    mode = "shadow"

    def __init__(self, auto_fill: bool = False, config: dict[str, Any] | None = None) -> None:
        resolved_config = dict(config or {})
        self._auto_fill = bool(resolved_config.get("auto_fill", auto_fill))
        self._filled_at = str(resolved_config.get("filled_at", "1970-01-01 00:00:00"))
        self._orders: list[dict[str, Any]] = []
        self._fills: list[dict[str, Any]] = []

    def place_order(self, intent: dict[str, Any]) -> dict[str, Any]:
        order = dict(intent)
        self._orders.append(order)
        shadow_order_id = f"shadow-{len(self._orders):04d}"
        result = {
            "result": "shadow_accepted",
            "shadow_order_id": shadow_order_id,
        }
        if self._auto_fill:
            fill = self._build_fill(intent=order, shadow_order_id=shadow_order_id)
            self._fills.append(fill)
            result["shadow_fill_id"] = fill["fill_id"]
        return result

    def cancel_order(self, order_id: str) -> dict[str, Any]:
        return {"result": "shadow_cancelled", "order_id": order_id}

    def query_orders(self) -> list[dict[str, Any]]:
        return [dict(item) for item in self._orders]

    def query_fills(self) -> list[dict[str, Any]]:
        return [dict(item) for item in self._fills]

    def _build_fill(self, intent: dict[str, Any], shadow_order_id: str) -> dict[str, Any]:
        quantity = intent.get("quantity", intent.get("qty", 0))
        price = intent.get("price", intent.get("limit_price", 0.0))
        return {
            "fill_id": f"{shadow_order_id}-F001",
            "order_id": shadow_order_id,
            "symbol": intent.get("symbol"),
            "quantity": quantity,
            "price": price,
            "filled_at": self._filled_at,
        }
