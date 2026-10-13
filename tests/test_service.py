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


def test_comments_are_listed_oldest_first(service):
    ticket = service.create_ticket("t", "", "alice")
    service.add_comment(ticket.id, "bob", "first")
    service.add_comment(ticket.id, "carol", "second")
    assert [c.body for c in service.comments(ticket.id)] == ["first", "second"]


@pytest.mark.parametrize("body", ["", "   \n"])
def test_empty_comments_are_rejected(service, body):
    ticket = service.create_ticket("t", "", "alice")
    with pytest.raises(ValueError, match="cannot be empty"):
        service.add_comment(ticket.id, "bob", body)


def test_comment_length_limit_is_inclusive(service):
    from tickets.service import MAX_COMMENT

    ticket = service.create_ticket("t", "", "alice")
    assert service.add_comment(ticket.id, "bob", "x" * MAX_COMMENT)
    with pytest.raises(ValueError, match="at most"):
        service.add_comment(ticket.id, "bob", "x" * (MAX_COMMENT + 1))


def test_commenting_on_an_unknown_ticket_fails(service):
    with pytest.raises(TicketNotFound):
        service.add_comment(999, "bob", "hello")
