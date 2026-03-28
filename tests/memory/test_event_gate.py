from src.memory.event_gate import gate_memory_score, should_persist


def test_gate_memory_score_respects_thresholds():
    assert gate_memory_score(0.9) == "confirmed"
    assert gate_memory_score(0.7) == "provisional"
    assert gate_memory_score(0.5) == "rejected"


def test_should_persist_only_for_provisional_or_higher():
    assert should_persist(0.9) is True
    assert should_persist(0.65) is True
    assert should_persist(0.64) is False

