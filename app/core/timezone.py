"""Timezone constants and helpers.

Persist datetimes in **UTC** in the database; use ``APP_TIMEZONE`` when you need
**Asia/Manila** (UTC+8) for display or business-local timestamps.
"""

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

__all__ = ["APP_TIMEZONE", "UTC", "now_app", "now_utc"]

APP_TIMEZONE = ZoneInfo("Asia/Manila")


def now_utc() -> datetime:
    return datetime.now(UTC)


def now_app() -> datetime:
    """Current wall-clock time in Asia/Manila."""
    return datetime.now(APP_TIMEZONE)
