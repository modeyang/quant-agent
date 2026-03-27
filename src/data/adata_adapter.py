from __future__ import annotations

from src.common.models import Asset, Bar


class AdataAdapter:
    def __init__(self, adata_module) -> None:
        self.adata = adata_module

    def get_daily_bars(self, symbols: list[str], start: str, end: str) -> list[Bar]:
        bars: list[Bar] = []
        for symbol in symbols:
            rows = self.adata.stock.market.get_market(
                stock_code=symbol,
                start_date=start,
                end_date=end,
                k_type=1,
                adjust_type=1,
            )
            for row in rows:
                bars.append(
                    Bar(
                        symbol=symbol,
                        ts=row["trade_date"],
                        open=float(row["open"]),
                        high=float(row["high"]),
                        low=float(row["low"]),
                        close=float(row["close"]),
                        volume=float(row["volume"]),
                    )
                )
        return bars

    def get_intraday_bars(self, symbols: list[str], trade_date: str) -> list[Bar]:
        return []

    def get_asset_master(self) -> list[Asset]:
        rows = self.adata.stock.info.all_code()
        return [
            Asset(
                symbol=row["stock_code"],
                asset_type="stock",
                exchange=row["stock_code"].split(".")[-1],
                name=row.get("short_name"),
            )
            for row in rows
        ]
