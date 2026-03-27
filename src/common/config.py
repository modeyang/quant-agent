from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(slots=True)
class AgentSettings:
    mode: str
    confirmation_threshold: float


@dataclass(slots=True)
class RiskSettings:
    max_position_pct: float
    max_daily_loss_pct: float
    max_drawdown_pct: float
    max_total_position_pct: float


@dataclass(slots=True)
class DataSourceSettings:
    enabled: bool
    cache_ttl: int


@dataclass(slots=True)
class DataSettings:
    akshare: DataSourceSettings
    adata: DataSourceSettings


@dataclass(slots=True)
class QmtSettings:
    enabled: bool
    reconnect_interval: int
    order_timeout: int
    max_retry: int


@dataclass(slots=True)
class StrategySettings:
    enabled: bool
    lookback_period: int
    entry_threshold: float
    stop_loss: float
    exit_threshold: float | None = None


@dataclass(slots=True)
class LoggingSettings:
    level: str
    rotation: str
    retention: int
    trade_log: bool


@dataclass(slots=True)
class Settings:
    agent: AgentSettings
    risk: RiskSettings
    data: DataSettings
    qmt: QmtSettings
    strategies: dict[str, StrategySettings]
    logging: LoggingSettings

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Settings":
        strategies = {
            name: StrategySettings(**values)
            for name, values in raw["strategies"].items()
        }
        return cls(
            agent=AgentSettings(**raw["agent"]),
            risk=RiskSettings(**raw["risk"]),
            data=DataSettings(
                akshare=DataSourceSettings(**raw["data"]["akshare"]),
                adata=DataSourceSettings(**raw["data"]["adata"]),
            ),
            qmt=QmtSettings(**raw["qmt"]),
            strategies=strategies,
            logging=LoggingSettings(**raw["logging"]),
        )


def load_settings(path: str | Path) -> Settings:
    with Path(path).open("r", encoding="utf-8") as file:
        raw = yaml.safe_load(file)
    return Settings.from_dict(raw)

