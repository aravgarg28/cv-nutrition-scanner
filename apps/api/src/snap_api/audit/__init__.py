"""Audit module: append-only record of security-relevant events.

Rows are insert-only (docs/architecture/DATA_MODEL.md §audit_event). The app layer
never updates or deletes them; revoking UPDATE/DELETE grants from the app DB role is
a deployment hardening step.
"""
