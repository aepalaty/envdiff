"""Detect key name collisions when env files are merged case-insensitively."""
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class CollisionEntry:
    canonical: str
    variants: List[str]
    envs: List[str]

    def __str__(self) -> str:
        variants_str = ", ".join(self.variants)
        envs_str = ", ".join(self.envs)
        return f"{self.canonical}: [{variants_str}] in [{envs_str}]"


@dataclass
class CollisionReport:
    env_names: List[str]
    entries: List[CollisionEntry] = field(default_factory=list)

    @property
    def has_collisions(self) -> bool:
        return len(self.entries) > 0

    @property
    def collision_keys(self) -> List[str]:
        return [e.canonical for e in self.entries]


class KeyCollisionDetector:
    """Detect keys that differ only by case across or within env files."""

    def calculate(
        self, envs: Dict[str, Dict[str, str]]
    ) -> CollisionReport:
        env_names = list(envs.keys())
        report = CollisionReport(env_names=env_names)

        # Build map: lowercase -> list of (original_key, env_name)
        lower_map: Dict[str, List[tuple]] = {}
        for env_name, env in envs.items():
            for key in env:
                lower = key.lower()
                lower_map.setdefault(lower, []).append((key, env_name))

        for lower, occurrences in lower_map.items():
            unique_variants = list(dict.fromkeys(k for k, _ in occurrences))
            if len(unique_variants) > 1:
                envs_involved = list(dict.fromkeys(e for _, e in occurrences))
                entry = CollisionEntry(
                    canonical=lower,
                    variants=unique_variants,
                    envs=envs_involved,
                )
                report.entries.append(entry)

        report.entries.sort(key=lambda e: e.canonical)
        return report
