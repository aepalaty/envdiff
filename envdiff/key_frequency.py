from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class FrequencyEntry:
    key: str
    count: int
    envs: List[str]

    @property
    def frequency(self) -> float:
        return self.count / max(len(self.envs), 1)

    def __str__(self) -> str:
        return f"{self.key}: {self.count} env(s) — {', '.join(self.envs)}"


@dataclass
class FrequencyReport:
    entries: List[FrequencyEntry] = field(default_factory=list)
    total_envs: int = 0

    def most_common(self, n: int = 10) -> List[FrequencyEntry]:
        return sorted(self.entries, key=lambda e: e.count, reverse=True)[:n]

    def least_common(self, n: int = 10) -> List[FrequencyEntry]:
        return sorted(self.entries, key=lambda e: e.count)[:n]

    def universal_keys(self) -> List[FrequencyEntry]:
        return [e for e in self.entries if e.count == self.total_envs]

    def unique_keys(self) -> List[FrequencyEntry]:
        return [e for e in self.entries if e.count == 1]


class KeyFrequencyCalculator:
    def calculate(self, envs: Dict[str, Dict[str, str]]) -> FrequencyReport:
        key_to_envs: Dict[str, List[str]] = {}

        for env_name, env_data in envs.items():
            for key in env_data:
                key_to_envs.setdefault(key, []).append(env_name)

        entries = [
            FrequencyEntry(key=k, count=len(v), envs=sorted(v))
            for k, v in sorted(key_to_envs.items())
        ]

        return FrequencyReport(entries=entries, total_envs=len(envs))
