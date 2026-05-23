from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class SymmetryEntry:
    key: str
    present_in: List[str]
    absent_from: List[str]

    def is_symmetric(self) -> bool:
        return len(self.absent_from) == 0

    def __str__(self) -> str:
        if self.is_symmetric():
            return f"{self.key}: present in all environments"
        missing = ", ".join(self.absent_from)
        return f"{self.key}: missing from [{missing}]"


@dataclass
class SymmetryReport:
    env_names: List[str]
    entries: List[SymmetryEntry] = field(default_factory=list)

    def asymmetric_keys(self) -> List[str]:
        return [e.key for e in self.entries if not e.is_symmetric()]

    def symmetric_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.is_symmetric()]

    def has_asymmetry(self) -> bool:
        return len(self.asymmetric_keys()) > 0

    def symmetry_ratio(self) -> float:
        if not self.entries:
            return 1.0
        return len(self.symmetric_keys()) / len(self.entries)


class SymmetryCalculator:
    def calculate(self, envs: Dict[str, Dict[str, str]]) -> SymmetryReport:
        env_names = list(envs.keys())
        all_keys: Set[str] = set()
        for env in envs.values():
            all_keys.update(env.keys())

        entries: List[SymmetryEntry] = []
        for key in sorted(all_keys):
            present_in = [name for name, env in envs.items() if key in env]
            absent_from = [name for name in env_names if name not in present_in]
            entries.append(SymmetryEntry(
                key=key,
                present_in=present_in,
                absent_from=absent_from,
            ))

        return SymmetryReport(env_names=env_names, entries=entries)
