import pytest

from tickets.models import Status, Ticket
from tickets.store import TicketStore


def make(title="t", **kw):
    return Ticket(id=0, title=title, description="d", reporter="alice", **kw)


def test_add_and_get_round_trip():
    store = TicketStore()
    added = store.add(make("Login fails"))
    assert store.get(added.id).title == "Login fails"
    with pytest.raises(KeyError):
        store.get(12345)


def test_list_by_status():
    store = TicketStore()
    a = store.add(make("a"))
    b = store.add(make("b"))
    b.status = Status.CLOSED
    store.save(b)
    assert [t.id for t in store.list_by_status(Status.OPEN)] == [a.id]


def test_search_title_is_a_substring_match_and_safe_with_quotes():
    store = TicketStore()
    store.add(make("Printer jams"))
    store.add(make("It's broken"))
    assert [t.title for t in store.search_title("jam")] == ["Printer jams"]
    assert [t.title for t in store.search_title("'")] == ["It's broken"]
