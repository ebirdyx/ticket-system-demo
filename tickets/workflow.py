"""Which status changes are allowed."""

from __future__ import annotations

from dataclasses import replace

from .models import Status, Ticket

ALLOWED: dict[Status, set[Status]] = {
    Status.OPEN: {Status.IN_PROGRESS, Status.CLOSED},
    Status.IN_PROGRESS: {Status.OPEN, Status.RESOLVED},
    Status.RESOLVED: {Status.OPEN, Status.CLOSED},
    Status.CLOSED: set(),
}


class InvalidTransition(Exception):
    """The requested status change is not allowed from the current status."""


def transition(ticket: Ticket, new_status: Status) -> Ticket:
    """Return a copy of `ticket` moved to `new_status`, or raise InvalidTransition. The argument is not modified."""
    if new_status not in ALLOWED[ticket.status]:
        raise InvalidTransition(f"cannot go from {ticket.status.value} to {new_status.value}")
    return replace(ticket, status=new_status)
