# ticket-system-demo

A small ticket tracker (create, assign, change status, search). **Synthetic project**, written to demonstrate an AI
code-review agent (MGL805 course project: https://github.com/ebirdyx/code-review-agent). It is not production code.

Run the tests: `uv run pytest -q`.

Layout: `tickets/models.py` (data), `tickets/store.py` (SQLite), `tickets/workflow.py` (allowed status changes),
`tickets/service.py` (business rules). Team rules for reviews: `.review-agent/rules.md`.

Pull requests in this repository come with their requirements (a Jira-style ticket) so the agent can check the code against them.
