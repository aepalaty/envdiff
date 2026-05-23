from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class BalanceEntry:
    key: str
    present_in: List[str]
    absent_from: List[str]

    @property
    def balance_ratio(self) -> float:
        total = len(self.present_in) + len(self.absent_from)
        if total == 0:
            return 0.0
        return len(self.present_in) / total

    @property
    def is_balanced(self) -> bool:
        return len(self.absent_from) == 0

    def __str__(self) -> str:
        ratio = self.balance_ratio
        status = "balanced" if self.is_balanced else f"missing from {len(self.absent_from)} env(s)"
        return f"{self.key}: {ratio:.0%} coverage ({status})"


@dataclass
class BalanceReport:
    env_names: List[str]
    entries: List[BalanceEntry] = field(default_factory=list)

    @property
    def unbalanced_keys(self) -> List[BalanceEntry]:
        return [e for e in self.entries if not e.is_balanced]

    @property
    def has_imbalance(self) -> bool:
        return len(self.unbalanced_keys) > 0

    @property
    def average_balance(self) -> float:
        if not self.entries:
            return 1.0
        return sum(e.balance_ratio for e in self.entries) / len(self.entries)


class BalanceCalculator:
    def calculate(self, envs: Dict[str, Dict[str, str]]) -> BalanceReport:
        env_names = list(envs.keys())
        all_keys: set = set()
        for env_data in envs.values():
            all_keys.update(env_data.keys())

        entries: List[BalanceEntry] = []
        for key in sorted(all_keys):
            present_in = [name for name, data in envs.items() if key in data]
            absent_from = [name for name in env_names if name not in present_in]
            entries.append(BalanceEntry(
                key=key,
                present_in=present_in,
                absent_from=absent_from,
            ))

        return BalanceReport(env_names=env_names, entries=entries)
