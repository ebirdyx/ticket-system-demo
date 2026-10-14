"""Business operations on tickets."""

from __future__ import annotations

from .models import Priority, Status, Ticket
from .store import TicketStore
from .workflow import transition

MAX_TITLE = 120


class TicketNotFound(Exception):
    pass


class TicketService:
    def __init__(self, store: TicketStore):
        self.store = store

    def create_ticket(self, title: str, description: str, reporter: str, priority: Priority = Priority.MEDIUM) -> Ticket:
        """Create an open ticket. The title is kept exactly as typed; it is required and at most MAX_TITLE characters."""
        if not title:
            raise ValueError("a ticket needs a title")
        if len(title) > MAX_TITLE:
            raise ValueError(f"the title is longer than {MAX_TITLE} characters")
        return self.store.add(Ticket(id=0, title=title, description=description, reporter=reporter, priority=priority))

    def get(self, ticket_id: int) -> Ticket:
        ticket = self.store.get(ticket_id)
        if ticket is None:
            raise TicketNotFound(ticket_id)
        return ticket

    def assign(self, ticket_id: int, assignee: str) -> Ticket:
        ticket = self.get(ticket_id)
        ticket.assignee = assignee
        self.store.save(ticket)
        return ticket

    def change_status(self, ticket_id: int, new_status: Status) -> Ticket:
        ticket = self.get(ticket_id)
        transition(ticket, new_status)
        self.store.save(ticket)
        return ticket
