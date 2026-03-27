from src.execution.approval import require_manual_approval


def test_new_position_requires_manual_approval():
    assert require_manual_approval(action="open", approved=False) is True


def test_explicit_approval_clears_manual_gate():
    assert require_manual_approval(action="open", approved=True) is False
