import pytest

from src.execution.order_state_machine import OrderStateMachine


def test_order_state_machine_blocks_duplicate_submission():
    sm = OrderStateMachine(plan_id="plan-1")

    sm.approve()
    sm.submit()

    assert sm.can_submit() is False


def test_order_state_machine_allows_reconcile_after_fill():
    sm = OrderStateMachine(plan_id="plan-1")

    sm.approve()
    sm.submit()
    sm.fill()
    sm.reconcile()

    assert sm.state == "reconciled"


def test_order_state_machine_rejects_invalid_transition():
    sm = OrderStateMachine(plan_id="plan-1")

    with pytest.raises(ValueError):
        sm.submit()
