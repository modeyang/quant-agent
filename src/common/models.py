from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Asset:
    symbol: str
    asset_type: str
    exchange: str | None = None
    name: str | None = None


@dataclass(slots=True)
class Bar:
    symbol: str
    ts: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    interval: str = "1d"


@dataclass(slots=True)
class CandidatePlan:
    symbol: str
    asset_type: str
    score: float
    status: str = "planned"
    notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class OrderIntent:
    symbol: str
    action: str
    quantity: int
    limit_price: float | None = None
    status: str = "draft"


@dataclass(slots=True)
class ReviewSummary:
    trade_date: str
    planned_count: int
    executed_count: int
    rejected_count: int
    notes: list[str] = field(default_factory=list)

