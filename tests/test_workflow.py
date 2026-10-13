import pytest

from tickets.models import Status, Ticket
from tickets.workflow import ALLOWED, InvalidTransition, transition


def ticket(status):
    return Ticket(id=1, title="t", description="", reporter="alice", status=status)


@pytest.mark.parametrize(("start", "end"), [(s, e) for s, targets in ALLOWED.items() for e in targets])
def test_allowed_transitions(start, end):
    t = ticket(start)
    transition(t, end)
    assert t.status is end


def test_closed_is_final():
    for target in Status:
        with pytest.raises(InvalidTransition):
            transition(ticket(Status.CLOSED), target)


def test_open_cannot_jump_to_resolved():
    with pytest.raises(InvalidTransition, match="open to resolved"):
        transition(ticket(Status.OPEN), Status.RESOLVED)
