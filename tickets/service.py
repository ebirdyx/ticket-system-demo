"""Business operations on tickets."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from .models import Priority, Status, Ticket
from .store import TicketStore
from .workflow import transition

MAX_TITLE = 120
ESCALATION_AGE = timedelta(hours=48)
PRIORITY_ORDER = [Priority.LOW, Priority.MEDIUM, Priority.HIGH, Priority.URGENT]


class TicketNotFound(Exception):
    pass


class TicketService:
    def __init__(self, store: TicketStore):
        self.store = store

    def create_ticket(self, title: str, description: str, reporter: str, priority: Priority = Priority.MEDIUM) -> Ticket:
        """Create an open ticket. The title is required and at most MAX_TITLE characters."""
        title = title.strip()
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

    def escalate_stale(self, now: datetime | None = None) -> list[Ticket]:
        """Raise the priority of open tickets that are old enough. Returns the tickets that were changed."""
        now = now or datetime.now(UTC)
        changed = []
        for ticket in self.store.list_by_status(Status.OPEN):
            if now - ticket.created_at > ESCALATION_AGE:
                index = PRIORITY_ORDER.index(ticket.priority)
                if index < len(PRIORITY_ORDER) - 1:
                    ticket.priority = PRIORITY_ORDER[index + 1]
                    self.store.save(ticket)
                    changed.append(ticket)
        return changed

    def change_status(self, ticket_id: int, new_status: Status) -> Ticket:
        ticket = self.get(ticket_id)
        transition(ticket, new_status)
        self.store.save(ticket)
        return ticket
