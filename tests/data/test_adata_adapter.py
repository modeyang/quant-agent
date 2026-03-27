from src.data.adata_adapter import AdataAdapter


def test_adata_adapter_maps_daily_bars(fake_adata_module):
    adapter = AdataAdapter(fake_adata_module)

    rows = adapter.get_daily_bars(["600000.SH"], "2026-03-01", "2026-03-10")

    assert len(rows) == 1
    assert rows[0].symbol == "600000.SH"
    assert rows[0].close == 10.2
