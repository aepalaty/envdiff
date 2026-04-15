from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class HeatmapCell:
    env_name: str
    key: str
    value: str
    present: bool
    is_sensitive: bool

    def __str__(self) -> str:
        status = "present" if self.present else "missing"
        return f"{self.env_name}/{self.key}: {status}"


@dataclass
class HeatmapReport:
    keys: List[str]
    env_names: List[str]
    cells: Dict[Tuple[str, str], HeatmapCell] = field(default_factory=dict)

    def coverage_for_key(self, key: str) -> float:
        present = sum(
            1 for env in self.env_names
            if self.cells.get((env, key), HeatmapCell("", "", "", False, False)).present
        )
        return present / len(self.env_names) if self.env_names else 0.0

    def coverage_for_env(self, env_name: str) -> float:
        present = sum(
            1 for key in self.keys
            if self.cells.get((env_name, key), HeatmapCell("", "", "", False, False)).present
        )
        return present / len(self.keys) if self.keys else 0.0

    def missing_in_env(self, env_name: str) -> List[str]:
        return [
            key for key in self.keys
            if not self.cells.get((env_name, key), HeatmapCell("", "", "", False, False)).present
        ]


_SENSITIVE_PATTERNS = ("password", "secret", "token", "key", "auth", "api_key", "private")


class HeatmapCalculator:
    def _is_sensitive(self, key: str) -> bool:
        lower = key.lower()
        return any(pat in lower for pat in _SENSITIVE_PATTERNS)

    def calculate(self, envs: Dict[str, Dict[str, str]]) -> HeatmapReport:
        env_names = list(envs.keys())
        all_keys = sorted({key for env in envs.values() for key in env})
        cells: Dict[Tuple[str, str], HeatmapCell] = {}

        for env_name, env_data in envs.items():
            for key in all_keys:
                present = key in env_data
                value = env_data.get(key, "")
                cells[(env_name, key)] = HeatmapCell(
                    env_name=env_name,
                    key=key,
                    value=value,
                    present=present,
                    is_sensitive=self._is_sensitive(key),
                )

        return HeatmapReport(keys=all_keys, env_names=env_names, cells=cells)
