"""Data model of the ticket tracker."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum


class Status(StrEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Priority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Comment:
    id: int
    ticket_id: int
    author: str
    body: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class Ticket:
    id: int
    title: str
    description: str
    reporter: str
    priority: Priority = Priority.MEDIUM
    status: Status = Status.OPEN
    assignee: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
