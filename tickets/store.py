"""SQLite storage for tickets. All SQL uses bound parameters."""

from __future__ import annotations

import sqlite3
from datetime import datetime

from .models import Comment, Priority, Status, Ticket

SCHEMA = """
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    reporter TEXT NOT NULL,
    priority TEXT NOT NULL,
    status TEXT NOT NULL,
    assignee TEXT,
    created_at TEXT NOT NULL
)
"""


COMMENTS_SCHEMA = """
CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id INTEGER NOT NULL REFERENCES tickets(id),
    author TEXT NOT NULL,
    body TEXT NOT NULL,
    created_at TEXT NOT NULL
)
"""


class TicketStore:
    def __init__(self, path: str = ":memory:"):
        self._db = sqlite3.connect(path)
        self._db.row_factory = sqlite3.Row
        self._db.execute(SCHEMA)
        self._db.execute(COMMENTS_SCHEMA)

    def add(self, ticket: Ticket) -> Ticket:
        """Insert a ticket and return it with its new id."""
        cursor = self._db.execute(
            "INSERT INTO tickets (title, description, reporter, priority, status, assignee, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (ticket.title, ticket.description, ticket.reporter, ticket.priority.value, ticket.status.value,
             ticket.assignee, ticket.created_at.isoformat()),
        )
        self._db.commit()
        ticket.id = cursor.lastrowid
        return ticket

    def get(self, ticket_id: int) -> Ticket | None:
        row = self._db.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        return _from_row(row) if row else None

    def save(self, ticket: Ticket) -> None:
        self._db.execute(
            "UPDATE tickets SET title = ?, description = ?, priority = ?, status = ?, assignee = ? WHERE id = ?",
            (ticket.title, ticket.description, ticket.priority.value, ticket.status.value, ticket.assignee, ticket.id),
        )
        self._db.commit()

    def list_by_status(self, status: Status) -> list[Ticket]:
        rows = self._db.execute("SELECT * FROM tickets WHERE status = ? ORDER BY id", (status.value,)).fetchall()
        return [_from_row(r) for r in rows]

    def search_title(self, term: str) -> list[Ticket]:
        rows = self._db.execute(
            "SELECT * FROM tickets WHERE title LIKE ? ORDER BY id", (f"%{term}%",)
        ).fetchall()
        return [_from_row(r) for r in rows]


    def add_comment(self, comment: Comment) -> Comment:
        """Insert a comment and return it with its new id."""
        cursor = self._db.execute(
            "INSERT INTO comments (ticket_id, author, body, created_at) VALUES (?, ?, ?, ?)",
            (comment.ticket_id, comment.author, comment.body, comment.created_at.isoformat()),
        )
        self._db.commit()
        comment.id = cursor.lastrowid
        return comment

    def list_comments(self, ticket_id: int) -> list[Comment]:
        """Comments of a ticket, oldest first."""
        rows = self._db.execute("SELECT * FROM comments WHERE ticket_id = ? ORDER BY id", (ticket_id,)).fetchall()
        return [
            Comment(id=r["id"], ticket_id=r["ticket_id"], author=r["author"], body=r["body"],
                    created_at=datetime.fromisoformat(r["created_at"]))
            for r in rows
        ]


def _from_row(row: sqlite3.Row) -> Ticket:
    return Ticket(
        id=row["id"], title=row["title"], description=row["description"], reporter=row["reporter"],
        priority=Priority(row["priority"]), status=Status(row["status"]), assignee=row["assignee"],
        created_at=datetime.fromisoformat(row["created_at"]),
    )
