from src.data.provider_base import MarketDataProvider


def test_market_data_provider_exposes_required_methods():
    required = {"get_daily_bars", "get_intraday_bars", "get_asset_master"}

    assert required.issubset(set(dir(MarketDataProvider)))

