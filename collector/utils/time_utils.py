"""
Time utilities for date handling.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional


class TimeUtils:
    """Helper for date parsing and formatting."""

    DATE_FORMATS = [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%d %b %Y",
        "%B %d, %Y",
        "%d %B %Y",
    ]

    @staticmethod
    def parse_date(date_str: str) -> Optional[datetime]:
        """Parse a date string with multiple format fallbacks."""
        if not date_str:
            return None

        for fmt in TimeUtils.DATE_FORMATS:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                # Make naive datetime offset-aware
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except (ValueError, TypeError):
                continue

        # Try dateutil parser as last resort
        try:
            from dateutil import parser
            return parser.parse(date_str)
        except (ImportError, ValueError, TypeError):
            pass

        return None

    @staticmethod
    def format_date(dt: datetime, fmt: str = "%Y-%m-%d") -> str:
        """Format a datetime to standard string."""
        return dt.strftime(fmt)

    @staticmethod
    def today_str() -> str:
        """Get today's date as YYYY-MM-DD string."""
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    @staticmethod
    def days_ago(n: int) -> datetime:
        """Get datetime from n days ago."""
        return datetime.now(timezone.utc) - timedelta(days=n)

    @staticmethod
    def is_within_days(date_str: str, days: int) -> bool:
        """Check if a date string is within the last N days."""
        dt = TimeUtils.parse_date(date_str)
        if dt is None:
            return False
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        return dt >= cutoff
