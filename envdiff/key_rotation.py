"""Detect keys that may need rotation based on age and sensitivity."""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from envdiff.key_age import AgeReport, AgeEntry
from envdiff.key_sensitivity import SensitivityReport, SensitivityEntry


@dataclass
class RotationEntry:
    key: str
    env_name: str
    days_since_change: int
    sensitivity_tier: str
    recommended_max_days: int

    @property
    def is_overdue(self) -> bool:
        return self.days_since_change > self.recommended_max_days

    @property
    def urgency(self) -> str:
        if not self.is_overdue:
            return "ok"
        ratio = self.days_since_change / max(self.recommended_max_days, 1)
        if ratio >= 2.0:
            return "critical"
        if ratio >= 1.5:
            return "high"
        return "medium"

    def __str__(self) -> str:
        status = f"overdue by {self.days_since_change - self.recommended_max_days}d" if self.is_overdue else "ok"
        return f"{self.key} [{self.env_name}]: {self.days_since_change}d old, tier={self.sensitivity_tier}, status={status}"


_TIER_MAX_DAYS: Dict[str, int] = {
    "critical": 30,
    "high": 60,
    "medium": 90,
    "low": 180,
}


@dataclass
class RotationReport:
    entries: List[RotationEntry] = field(default_factory=list)
    env_names: List[str] = field(default_factory=list)

    @property
    def overdue(self) -> List[RotationEntry]:
        return [e for e in self.entries if e.is_overdue]

    @property
    def has_overdue(self) -> bool:
        return bool(self.overdue)

    def by_urgency(self, urgency: str) -> List[RotationEntry]:
        return [e for e in self.overdue if e.urgency == urgency]


class RotationCalculator:
    def calculate(
        self,
        age_report: AgeReport,
        sensitivity_report: SensitivityReport,
    ) -> RotationReport:
        sensitivity_map: Dict[str, str] = {}
        for entry in sensitivity_report.entries:
            sensitivity_map[entry.key] = entry.tier

        entries: List[RotationEntry] = []
        env_names: List[str] = list({
            snap_name
            for age_entry in age_report.entries
            for snap_name in age_entry.snapshots_seen
        })

        for age_entry in age_report.entries:
            tier = sensitivity_map.get(age_entry.key, "low")
            max_days = _TIER_MAX_DAYS.get(tier, 180)
            days = age_entry.days_since_last_change
            for env in age_entry.snapshots_seen:
                entries.append(RotationEntry(
                    key=age_entry.key,
                    env_name=env,
                    days_since_change=days,
                    sensitivity_tier=tier,
                    recommended_max_days=max_days,
                ))

        return RotationReport(entries=entries, env_names=env_names)
