from datetime import datetime, timedelta

import pytest

from src.booking import can_reschedule, reschedule

NOW = datetime(2026, 1, 10, 9, 0)


def test_can_reschedule_with_more_than_24_hours_notice():
    assert can_reschedule(NOW + timedelta(hours=48), NOW)


def test_exactly_24_hours_notice_is_allowed():
    assert can_reschedule(NOW + timedelta(hours=24), NOW)


def test_reschedule_is_refused_with_less_than_24_hours_notice():
    with pytest.raises(ValueError, match="Too late"):
        reschedule(NOW + timedelta(hours=23), NOW + timedelta(days=3), NOW)
