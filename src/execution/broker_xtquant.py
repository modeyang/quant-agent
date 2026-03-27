from __future__ import annotations

from typing import Any


class XtquantBroker:
    def __init__(self, trader_client, account) -> None:
        self.trader_client = trader_client
        self.account = account

    def place_order(self, intent: dict[str, Any]) -> Any:
        return self.trader_client.order_stock(
            self.account,
            intent["symbol"],
            intent["side"],
            intent["quantity"],
            intent["price_type"],
            intent["price"],
            intent.get("strategy_name", "quant-agent"),
            intent.get("remark", ""),
        )

    def cancel_order(self, order_id: str) -> Any:
        return self.trader_client.cancel_order_stock(self.account, order_id)

    def query_orders(self) -> list[dict[str, Any]]:
        orders = self.trader_client.query_stock_orders(self.account)
        return [order for order in orders]
