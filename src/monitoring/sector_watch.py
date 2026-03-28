from __future__ import annotations


def assess_sector_rotation(sector_strength: dict[str, float]) -> dict[str, object]:
    if not sector_strength:
        return {
            "status": "pending",
            "leaders": [],
            "laggards": [],
            "summary": "sector data unavailable",
        }

    ranked = sorted(sector_strength.items(), key=lambda item: item[1], reverse=True)
    leaders = [name for name, _ in ranked[:2]]
    laggards = [name for name, _ in ranked[-2:]]
    return {
        "status": "ready",
        "leaders": leaders,
        "laggards": laggards,
        "summary": f"leaders: {', '.join(leaders)}; laggards: {', '.join(laggards)}",
    }

