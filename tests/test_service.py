from datetime import UTC, datetime, timedelta

import pytest

from tickets.models import Priority, Status
from tickets.service import MAX_TITLE, TicketNotFound, TicketService
from tickets.store import TicketStore
from tickets.workflow import InvalidTransition


@pytest.fixture
def service():
    return TicketService(TicketStore())


def test_create_ticket_is_open_and_gets_an_id(service):
    ticket = service.create_ticket("  Printer is broken ", "It jams.", "alice")
    assert ticket.id >= 1 and ticket.status is Status.OPEN and ticket.title == "Printer is broken"
    assert ticket.priority is Priority.MEDIUM


@pytest.mark.parametrize("title", ["", "   "])
def test_a_title_is_required(service, title):
    with pytest.raises(ValueError, match="needs a title"):
        service.create_ticket(title, "", "alice")


def test_title_length_limit_is_inclusive(service):
    assert service.create_ticket("x" * MAX_TITLE, "", "alice")
    with pytest.raises(ValueError, match="longer than"):
        service.create_ticket("x" * (MAX_TITLE + 1), "", "alice")


def test_assign_persists(service):
    ticket = service.create_ticket("t", "", "alice")
    service.assign(ticket.id, "bob")
    assert service.get(ticket.id).assignee == "bob"


def test_unknown_ticket(service):
    with pytest.raises(TicketNotFound):
        service.get(999)


def test_status_follows_the_workflow(service):
    ticket = service.create_ticket("t", "", "alice")
    service.change_status(ticket.id, Status.IN_PROGRESS)
    service.change_status(ticket.id, Status.RESOLVED)
    assert service.get(ticket.id).status is Status.RESOLVED
    with pytest.raises(InvalidTransition):
        service.change_status(ticket.id, Status.IN_PROGRESS)


NOW = datetime(2026, 10, 13, 12, 0, tzinfo=UTC)


def aged(service, hours, priority=Priority.MEDIUM):
    ticket = service.create_ticket("t", "", "alice", priority)
    ticket.created_at = NOW - timedelta(hours=hours)
    service.store._db.execute("UPDATE tickets SET created_at = ? WHERE id = ?", (ticket.created_at.isoformat(), ticket.id))
    return ticket


def test_an_old_open_ticket_is_escalated_one_level(service):
    ticket = aged(service, 72)
    assert [t.id for t in service.escalate_stale(NOW)] == [ticket.id]
    assert service.get(ticket.id).priority is Priority.HIGH


def test_a_recent_ticket_is_left_alone(service):
    ticket = aged(service, 1)
    assert service.escalate_stale(NOW) == []
    assert service.get(ticket.id).priority is Priority.MEDIUM


def test_urgent_stays_urgent(service):
    ticket = aged(service, 100, Priority.URGENT)
    assert service.escalate_stale(NOW) == []
    assert service.get(ticket.id).priority is Priority.URGENT


def test_tickets_that_are_not_open_are_never_escalated(service):
    ticket = aged(service, 100)
    service.change_status(ticket.id, Status.IN_PROGRESS)
    assert service.escalate_stale(NOW) == []
