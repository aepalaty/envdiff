"""Detect keys that appear to be inherited or overridden across environments."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class InheritanceEntry:
    key: str
    base_value: Optional[str]
    overrides: Dict[str, str] = field(default_factory=dict)  # env_name -> value

    @property
    def is_overridden(self) -> bool:
        return any(v != self.base_value for v in self.overrides.values())

    @property
    def override_envs(self) -> List[str]:
        return [env for env, val in self.overrides.items() if val != self.base_value]

    def __str__(self) -> str:
        if not self.is_overridden:
            return f"{self.key}: inherited in all environments"
        envs = ", ".join(self.override_envs)
        return f"{self.key}: overridden in [{envs}]"


@dataclass
class InheritanceReport:
    base_name: str
    entries: List[InheritanceEntry] = field(default_factory=list)

    @property
    def overridden_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.is_overridden]

    @property
    def inherited_keys(self) -> List[str]:
        return [e.key for e in self.entries if not e.is_overridden]

    @property
    def has_overrides(self) -> bool:
        return bool(self.overridden_keys)


class InheritanceDetector:
    def calculate(
        self,
        base_env: Dict[str, str],
        other_envs: Dict[str, Dict[str, str]],
        base_name: str = "base",
    ) -> InheritanceReport:
        report = InheritanceReport(base_name=base_name)
        all_keys = set(base_env.keys())
        for env in other_envs.values():
            all_keys.update(env.keys())

        for key in sorted(all_keys):
            base_value = base_env.get(key)
            overrides: Dict[str, str] = {}
            for env_name, env_data in other_envs.items():
                if key in env_data:
                    overrides[env_name] = env_data[key]
            entry = InheritanceEntry(
                key=key,
                base_value=base_value,
                overrides=overrides,
            )
            report.entries.append(entry)

        return report
