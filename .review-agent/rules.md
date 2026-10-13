# Team coding rules

1. All SQL uses bound parameters (`?`). Never build SQL with f-strings, `%` or `+`.
2. Never silence an exception: catch the narrowest type, and log or re-raise it. `except Exception: pass` is not allowed.
3. Public functions have type hints and a one-line docstring that says what they return or raise.
4. Every change in behaviour comes with a test, including the boundary values (for example "exactly 48 hours").
5. Permission checks live in the service layer, not in the callers.
