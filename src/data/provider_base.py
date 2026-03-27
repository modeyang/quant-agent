from __future__ import annotations

from typing import Protocol

from src.common.models import Asset, Bar


class MarketDataProvider(Protocol):
    def get_daily_bars(self, symbols: list[str], start: str, end: str) -> list[Bar]:
        ...

    def get_intraday_bars(self, symbols: list[str], trade_date: str) -> list[Bar]:
        ...

    def get_asset_master(self) -> list[Asset]:
        ...
