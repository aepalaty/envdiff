"""Measures the density of populated (non-empty) keys across environments."""
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DensityEntry:
    key: str
    total_envs: int
    populated_count: int
    empty_count: int
    missing_count: int

    @property
    def density_ratio(self) -> float:
        """Fraction of envs where the key has a non-empty value."""
        if self.total_envs == 0:
            return 0.0
        return self.populated_count / self.total_envs

    @property
    def is_sparse(self) -> bool:
        return self.density_ratio < 0.5

    def __str__(self) -> str:
        pct = int(self.density_ratio * 100)
        return (
            f"{self.key}: {pct}% populated "
            f"({self.populated_count}/{self.total_envs} envs)"
        )


@dataclass
class DensityReport:
    env_names: List[str]
    entries: List[DensityEntry] = field(default_factory=list)

    @property
    def sparse_keys(self) -> List[DensityEntry]:
        return [e for e in self.entries if e.is_sparse]

    @property
    def fully_populated_keys(self) -> List[DensityEntry]:
        return [e for e in self.entries if e.density_ratio == 1.0]

    def entry_for(self, key: str) -> DensityEntry | None:
        return next((e for e in self.entries if e.key == key), None)


class DensityCalculator:
    """Calculate key density across multiple environments."""

    def calculate(self, envs: Dict[str, Dict[str, str]]) -> DensityReport:
        env_names = list(envs.keys())
        total = len(env_names)
        all_keys: set = set()
        for env in envs.values():
            all_keys.update(env.keys())

        entries: List[DensityEntry] = []
        for key in sorted(all_keys):
            populated = 0
            empty = 0
            missing = 0
            for env in envs.values():
                if key not in env:
                    missing += 1
                elif env[key].strip() == "":
                    empty += 1
                else:
                    populated += 1
            entries.append(
                DensityEntry(
                    key=key,
                    total_envs=total,
                    populated_count=populated,
                    empty_count=empty,
                    missing_count=missing,
                )
            )

        return DensityReport(env_names=env_names, entries=entries)
