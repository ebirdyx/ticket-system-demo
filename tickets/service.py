"""Business operations on tickets."""

from __future__ import annotations

from .models import Comment, Priority, Status, Ticket
from .store import TicketStore
from .workflow import transition

MAX_TITLE = 120
MAX_COMMENT = 2000


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

    def add_comment(self, ticket_id: int, author: str, body: str) -> Comment:
        """Add a comment to an existing ticket. Raises ValueError if it is empty or longer than MAX_COMMENT."""
        self.get(ticket_id)  # raises TicketNotFound
        body = body.strip()
        if not body:
            raise ValueError("a comment cannot be empty")
        if len(body) > MAX_COMMENT:
            raise ValueError(f"a comment is at most {MAX_COMMENT} characters")
        return self.store.add_comment(Comment(id=0, ticket_id=ticket_id, author=author, body=body))

    def comments(self, ticket_id: int) -> list[Comment]:
        """Comments of a ticket, oldest first."""
        self.get(ticket_id)
        return self.store.list_comments(ticket_id)

    def change_status(self, ticket_id: int, new_status: Status) -> Ticket:
        ticket = self.get(ticket_id)
        transition(ticket, new_status)
        self.store.save(ticket)
        return ticket
