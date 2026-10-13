"""Which status changes are allowed."""

from __future__ import annotations

from .models import Status, Ticket

ALLOWED: dict[Status, set[Status]] = {
    Status.OPEN: {Status.IN_PROGRESS, Status.CLOSED},
    Status.IN_PROGRESS: {Status.OPEN, Status.RESOLVED},
    Status.RESOLVED: {Status.OPEN, Status.CLOSED},
    Status.CLOSED: set(),
}


class InvalidTransition(Exception):
    """The requested status change is not allowed from the current status."""


def transition(ticket: Ticket, new_status: Status) -> None:
    """Move a ticket to `new_status`, or raise InvalidTransition."""
    if new_status not in ALLOWED[ticket.status]:
        raise InvalidTransition(f"cannot go from {ticket.status.value} to {new_status.value}")
    ticket.status = new_status
