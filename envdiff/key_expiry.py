from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Dict, List, Optional


DEFAULT_EXPIRY_DAYS = 90


@dataclass
class ExpiryEntry:
    key: str
    env_name: str
    last_rotated: Optional[date]
    expiry_days: int
    expires_on: Optional[date]

    def is_expired(self) -> bool:
        if self.expires_on is None:
            return False
        return date.today() >= self.expires_on

    def days_until_expiry(self) -> Optional[int]:
        if self.expires_on is None:
            return None
        return (self.expires_on - date.today()).days

    def __str__(self) -> str:
        if self.expires_on is None:
            return f"{self.key} ({self.env_name}): no expiry date"
        days = self.days_until_expiry()
        status = "EXPIRED" if self.is_expired() else f"expires in {days}d"
        return f"{self.key} ({self.env_name}): {status}"


@dataclass
class ExpiryReport:
    entries: List[ExpiryEntry] = field(default_factory=list)
    env_names: List[str] = field(default_factory=list)

    def expired_entries(self) -> List[ExpiryEntry]:
        return [e for e in self.entries if e.is_expired()]

    def expiring_soon(self, within_days: int = 14) -> List[ExpiryEntry]:
        return [
            e for e in self.entries
            if not e.is_expired()
            and e.days_until_expiry() is not None
            and e.days_until_expiry() <= within_days
        ]

    def has_issues(self) -> bool:
        return bool(self.expired_entries() or self.expiring_soon())


class ExpiryCalculator:
    """Detects expired or soon-to-expire keys based on rotation metadata."""

    def __init__(self, expiry_days: int = DEFAULT_EXPIRY_DAYS) -> None:
        self.expiry_days = expiry_days

    def calculate(
        self,
        envs: Dict[str, Dict[str, str]],
        rotation_dates: Optional[Dict[str, Dict[str, date]]] = None,
    ) -> ExpiryReport:
        """Calculate expiry for sensitive keys across environments.

        Args:
            envs: Mapping of env_name -> {key: value}.
            rotation_dates: Optional mapping of env_name -> {key: last_rotated date}.
        """
        rotation_dates = rotation_dates or {}
        entries: List[ExpiryEntry] = []
        env_names = list(envs.keys())

        for env_name, env in envs.items():
            dates_for_env = rotation_dates.get(env_name, {})
            for key in env:
                last_rotated = dates_for_env.get(key)
                if last_rotated is not None:
                    expires_on = last_rotated + timedelta(days=self.expiry_days)
                else:
                    expires_on = None
                entries.append(
                    ExpiryEntry(
                        key=key,
                        env_name=env_name,
                        last_rotated=last_rotated,
                        expiry_days=self.expiry_days,
                        expires_on=expires_on,
                    )
                )

        return ExpiryReport(entries=entries, env_names=env_names)
