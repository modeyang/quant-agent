from __future__ import annotations

from src.common.models import Asset, Bar


class XtdataAdapter:
    def __init__(self, xtdata_client) -> None:
        self.xtdata = xtdata_client

    def get_daily_bars(self, symbols: list[str], start: str, end: str) -> list[Bar]:
        data = self.xtdata.get_market_data_ex(
            field_list=[],
            stock_list=symbols,
            period="1d",
            start_time=start,
            end_time=end,
            dividend_type="front",
            fill_data=True,
        )
        bars: list[Bar] = []
        for symbol, rows in data.items():
            for row in rows:
                bars.append(
                    Bar(
                        symbol=symbol,
                        ts=str(row["time"]),
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
        return []
