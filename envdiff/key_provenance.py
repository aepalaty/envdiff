from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ProvenanceEntry:
    key: str
    sources: List[str] = field(default_factory=list)
    first_source: Optional[str] = None
    value_consistent: bool = True
    values_by_source: Dict[str, str] = field(default_factory=dict)

    def __str__(self) -> str:
        status = "consistent" if self.value_consistent else "inconsistent"
        return f"{self.key}: {len(self.sources)} source(s), {status}"


@dataclass
class ProvenanceReport:
    entries: List[ProvenanceEntry] = field(default_factory=list)
    env_names: List[str] = field(default_factory=list)

    def inconsistent_keys(self) -> List[str]:
        return [e.key for e in self.entries if not e.value_consistent]

    def keys_from_single_source(self) -> List[str]:
        return [e.key for e in self.entries if len(e.sources) == 1]

    def has_inconsistencies(self) -> bool:
        return len(self.inconsistent_keys()) > 0


class ProvenanceCalculator:
    def calculate(
        self, envs: Dict[str, Dict[str, str]]
    ) -> ProvenanceReport:
        env_names = list(envs.keys())
        all_keys: set = set()
        for env in envs.values():
            all_keys.update(env.keys())

        entries: List[ProvenanceEntry] = []
        for key in sorted(all_keys):
            sources = [name for name, env in envs.items() if key in env]
            values_by_source = {
                name: env[key] for name, env in envs.items() if key in env
            }
            unique_values = set(values_by_source.values())
            entry = ProvenanceEntry(
                key=key,
                sources=sources,
                first_source=sources[0] if sources else None,
                value_consistent=len(unique_values) <= 1,
                values_by_source=values_by_source,
            )
            entries.append(entry)

        return ProvenanceReport(entries=entries, env_names=env_names)
