"""Shared pytest fixtures for Quant Agent tests."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.common.models import Asset, Bar


@pytest.fixture
def fake_adata_module():
    stock_market = SimpleNamespace(
        get_market=lambda stock_code, start_date, end_date, k_type, adjust_type: [
            {
                "trade_date": "2026-03-03",
                "open": 10.0,
                "high": 10.5,
                "low": 9.8,
                "close": 10.2,
                "volume": 120000,
            }
        ]
    )
    stock_info = SimpleNamespace(
        all_code=lambda: [
            {
                "stock_code": "600000.SH",
                "short_name": "浦发银行",
            }
        ]
    )
    stock = SimpleNamespace(market=stock_market, info=stock_info)
    return SimpleNamespace(stock=stock)


@pytest.fixture
def fake_provider():
    class FakeProvider:
        def get_daily_bars(self, symbols, start, end):
            return [
                Bar(
                    symbol=symbols[0],
                    ts="2026-03-27",
                    open=10.0,
                    high=10.6,
                    low=9.9,
                    close=10.4,
                    volume=150000,
                )
            ]

        def get_intraday_bars(self, symbols, trade_date):
            return []

        def get_asset_master(self):
            return [Asset(symbol="600000.SH", asset_type="stock", exchange="SH", name="浦发银行")]

    return FakeProvider()


@pytest.fixture
def fake_broker():
    class FakeBroker:
        def __init__(self) -> None:
            self.placed_orders: list[dict[str, object]] = []

        def place_order(self, intent):
            self.placed_orders.append(dict(intent))
            return {"result": "ok", "order_count": len(self.placed_orders)}

        def cancel_order(self, order_id):
            return {"result": "ok", "order_id": order_id}

        def query_orders(self):
            return [dict(item) for item in self.placed_orders]

    return FakeBroker()
