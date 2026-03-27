from src.common.config import load_settings


def test_load_settings_reads_default_yaml():
    settings = load_settings("config/default.yaml")

    assert settings.agent.mode == "manual"
    assert settings.risk.max_position_pct == 0.20
    assert settings.data.adata.cache_ttl == 60

