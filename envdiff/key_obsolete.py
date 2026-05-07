"""Detect keys that appear in only one environment and may be obsolete."""
from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class ObsoleteEntry:
    key: str
    present_in: List[str]
    absent_from: List[str]

    def __str__(self) -> str:
        present = ", ".join(self.present_in)
        absent = ", ".join(self.absent_from)
        return f"{self.key}: present in [{present}], absent from [{absent}]"


@dataclass
class ObsoleteReport:
    env_names: List[str]
    entries: List[ObsoleteEntry] = field(default_factory=list)

    @property
    def has_obsolete(self) -> bool:
        return len(self.entries) > 0

    @property
    def obsolete_keys(self) -> List[str]:
        return [e.key for e in self.entries]

    def for_env(self, env_name: str) -> List[ObsoleteEntry]:
        return [e for e in self.entries if env_name in e.absent_from]


class ObsoleteDetector:
    """Identifies keys that appear in fewer than all environments."""

    def calculate(self, envs: Dict[str, Dict[str, str]]) -> ObsoleteReport:
        env_names = list(envs.keys())
        report = ObsoleteReport(env_names=env_names)

        all_keys: Set[str] = set()
        for env in envs.values():
            all_keys.update(env.keys())

        for key in sorted(all_keys):
            present_in = [name for name, env in envs.items() if key in env]
            absent_from = [name for name in env_names if key not in envs[name]]
            if absent_from:
                report.entries.append(
                    ObsoleteEntry(
                        key=key,
                        present_in=present_in,
                        absent_from=absent_from,
                    )
                )

        return report
