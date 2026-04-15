from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class CoverageEntry:
    key: str
    present_in: List[str]
    absent_from: List[str]

    @property
    def coverage_ratio(self) -> float:
        total = len(self.present_in) + len(self.absent_from)
        return len(self.present_in) / total if total > 0 else 0.0

    @property
    def is_universal(self) -> bool:
        return len(self.absent_from) == 0

    def __str__(self) -> str:
        pct = int(self.coverage_ratio * 100)
        return f"{self.key}: {pct}% ({len(self.present_in)}/{len(self.present_in) + len(self.absent_from)} envs)"


@dataclass
class CoverageReport:
    env_names: List[str]
    entries: List[CoverageEntry] = field(default_factory=list)

    @property
    def total_keys(self) -> int:
        return len(self.entries)

    @property
    def universal_keys(self) -> List[CoverageEntry]:
        return [e for e in self.entries if e.is_universal]

    @property
    def partial_keys(self) -> List[CoverageEntry]:
        return [e for e in self.entries if not e.is_universal]

    @property
    def average_coverage(self) -> float:
        if not self.entries:
            return 0.0
        return sum(e.coverage_ratio for e in self.entries) / len(self.entries)


class CoverageCalculator:
    def calculate(self, envs: Dict[str, Dict[str, str]]) -> CoverageReport:
        env_names = list(envs.keys())
        all_keys: Set[str] = set()
        for env in envs.values():
            all_keys.update(env.keys())

        entries: List[CoverageEntry] = []
        for key in sorted(all_keys):
            present_in = [name for name, env in envs.items() if key in env]
            absent_from = [name for name in env_names if name not in present_in]
            entries.append(CoverageEntry(key=key, present_in=present_in, absent_from=absent_from))

        return CoverageReport(env_names=env_names, entries=entries)
