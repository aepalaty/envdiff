from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class CompressionEntry:
    key: str
    original_size: int
    compressed_size: int
    ratio: float
    envs: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        return (
            f"{self.key}: {self.original_size}B -> {self.compressed_size}B "
            f"({self.ratio:.1%} ratio) in {len(self.envs)} env(s)"
        )

    @property
    def is_compressible(self) -> bool:
        return self.ratio < 0.8 and self.original_size >= 32


@dataclass
class CompressionReport:
    entries: List[CompressionEntry] = field(default_factory=list)
    env_names: List[str] = field(default_factory=list)

    @property
    def compressible_keys(self) -> List[CompressionEntry]:
        return [e for e in self.entries if e.is_compressible]

    @property
    def average_ratio(self) -> float:
        if not self.entries:
            return 1.0
        return sum(e.ratio for e in self.entries) / len(self.entries)

    def entry_for_key(self, key: str) -> Optional[CompressionEntry]:
        return next((e for e in self.entries if e.key == key), None)


class CompressionCalculator:
    """Estimates compressibility of env values using run-length heuristics."""

    def calculate(self, envs: Dict[str, Dict[str, str]]) -> CompressionReport:
        env_names = list(envs.keys())
        all_keys: set = set()
        for env in envs.values():
            all_keys.update(env.keys())

        entries: List[CompressionEntry] = []
        for key in sorted(all_keys):
            values_by_env: Dict[str, str] = {
                name: env[key] for name, env in envs.items() if key in env
            }
            if not values_by_env:
                continue

            total_original = sum(len(v) for v in values_by_env.values())
            total_compressed = sum(
                self._estimate_compressed(v) for v in values_by_env.values()
            )
            ratio = total_compressed / total_original if total_original > 0 else 1.0
            entries.append(
                CompressionEntry(
                    key=key,
                    original_size=total_original,
                    compressed_size=total_compressed,
                    ratio=ratio,
                    envs=list(values_by_env.keys()),
                )
            )

        return CompressionReport(entries=entries, env_names=env_names)

    def _estimate_compressed(self, value: str) -> int:
        """Simple run-length estimate of compressed byte size."""
        if not value:
            return 0
        runs = 1
        for i in range(1, len(value)):
            if value[i] != value[i - 1]:
                runs += 1
        return max(1, int(len(value) * (runs / len(value)) ** 0.5))
