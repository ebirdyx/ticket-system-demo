from datetime import date

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


def test_a_due_date_can_be_set_and_cleared(service):
    ticket = service.create_ticket("t", "", "alice")
    assert service.set_due_date(ticket.id, date(2026, 11, 1)).due_date == date(2026, 11, 1)
    assert service.get(ticket.id).due_date == date(2026, 11, 1)
    assert service.set_due_date(ticket.id, None).due_date is None


def test_overdue_tickets_are_listed(service):
    late = service.create_ticket("late", "", "alice")
    fine = service.create_ticket("fine", "", "alice")
    service.set_due_date(late.id, date(2026, 10, 1))
    service.set_due_date(fine.id, date(2026, 12, 1))
    assert [t.id for t in service.overdue(date(2026, 10, 13))] == [late.id]
