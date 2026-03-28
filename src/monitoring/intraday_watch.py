from __future__ import annotations

from typing import Any


def _symbol_of(item: Any) -> str | None:
    if isinstance(item, dict):
        return item.get("symbol")
    return getattr(item, "symbol", None)


def assess_intraday_watch(
    plans: list[Any],
    orders: list[dict[str, Any]],
    fills: list[dict[str, Any]],
) -> dict[str, Any]:
    planned_symbols = {symbol for symbol in (_symbol_of(plan) for plan in plans) if symbol}
    ordered_symbols = {
        order["symbol"]
        for order in orders
        if order.get("status") not in {"rejected", "canceled"}
    }
    filled_symbols = {fill["symbol"] for fill in fills}

    invalidated_symbols = sorted(planned_symbols - ordered_symbols)
    reinforced_symbols = sorted(planned_symbols & filled_symbols)

    if invalidated_symbols:
        status = "alert"
    elif reinforced_symbols:
        status = "reinforced"
    else:
        status = "neutral"

    notes: list[str] = []
    if invalidated_symbols:
        notes.append(f"invalidated symbols: {', '.join(invalidated_symbols)}")
    if reinforced_symbols:
        notes.append(f"reinforced symbols: {', '.join(reinforced_symbols)}")

    return {
        "status": status,
        "planned_count": len(planned_symbols),
        "ordered_count": len(ordered_symbols),
        "filled_count": len(filled_symbols),
        "invalidated_symbols": invalidated_symbols,
        "reinforced_symbols": reinforced_symbols,
        "notes": notes,
    }
