from __future__ import annotations

from dataclasses import dataclass


ALLOWED_TRANSITIONS = {
    "planned": {"approved"},
    "approved": {"submitted"},
    "submitted": {"partial_fill", "filled", "canceled", "rejected"},
    "partial_fill": {"filled", "canceled", "rejected", "reconciled"},
    "filled": {"reconciled"},
    "canceled": {"reconciled"},
    "rejected": {"reconciled"},
    "reconciled": {"reviewed"},
    "reviewed": set(),
}


@dataclass
class OrderStateMachine:
    plan_id: str
    state: str = "planned"

    def _transition(self, next_state: str) -> None:
        allowed = ALLOWED_TRANSITIONS.get(self.state, set())
        if next_state not in allowed:
            raise ValueError(f"cannot transition from {self.state} to {next_state}")
        self.state = next_state

    def can_submit(self) -> bool:
        return self.state == "approved"

    def approve(self) -> None:
        self._transition("approved")

    def submit(self) -> None:
        self._transition("submitted")

    def partial_fill(self) -> None:
        self._transition("partial_fill")

    def fill(self) -> None:
        self._transition("filled")

    def cancel(self) -> None:
        self._transition("canceled")

    def reject(self) -> None:
        self._transition("rejected")

    def reconcile(self) -> None:
        self._transition("reconciled")

    def review(self) -> None:
        self._transition("reviewed")
