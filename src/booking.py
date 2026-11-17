"""Tiny demo app: the rule for rescheduling a booking.

It exists so the gates in .claude/hooks/ have real code and real tests to guard.
"""
from datetime import datetime, timedelta

MIN_NOTICE = timedelta(hours=24)


def can_reschedule(starts_at: datetime, now: datetime) -> bool:
    """A booking can be moved only if it starts at least 24 hours from now."""
    return starts_at - now >= MIN_NOTICE


def reschedule(starts_at: datetime, new_start: datetime, now: datetime) -> datetime:
    """Return the new start time, or raise ValueError if the move is not allowed."""
    if not can_reschedule(starts_at, now):
        raise ValueError("Too late to reschedule: less than 24 hours' notice.")
    if new_start <= now:
        raise ValueError("The new time must be in the future.")
    return new_start
