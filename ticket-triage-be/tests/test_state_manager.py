import pytest

from ticket_triage.core.queue.state_manager import InvalidStateTransitionError, StateManager


def test_valid_transitions():
    assert StateManager.can_transition("new", "assigned") is True
    assert StateManager.can_transition("assigned", "in_progress") is True
    assert StateManager.can_transition("in_progress", "resolved") is True
    assert StateManager.can_transition("resolved", "new") is True

def test_invalid_transitions():
    assert StateManager.can_transition("new", "resolved") is False
    with pytest.raises(InvalidStateTransitionError):
        StateManager.validate_transition("new", "resolved")
