from __future__ import annotations

from typing import Any, Protocol


class Broker(Protocol):
    def place_order(self, intent: dict[str, Any]) -> Any:
        ...

    def cancel_order(self, order_id: str) -> Any:
        ...

    def query_orders(self) -> list[dict[str, Any]]:
        ...
