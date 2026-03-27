from __future__ import annotations


MANUAL_ACTIONS = {"open", "add", "cancel", "risk_stop"}


def require_manual_approval(action: str, approved: bool) -> bool:
    if action in MANUAL_ACTIONS and not approved:
        return True
    return False
