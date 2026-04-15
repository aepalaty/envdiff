"""Detect outlier keys — keys whose values deviate significantly from the norm across environments."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from collections import Counter


@dataclass
class OutlierEntry:
    key: str
    common_value: Optional[str]
    outlier_envs: Dict[str, str]  # env_name -> value that differs

    def __str__(self) -> str:
        parts = [f"{self.key}: common={self.common_value!r}"]
        for env, val in self.outlier_envs.items():
            parts.append(f"  {env}: {val!r}")
        return "\n".join(parts)


@dataclass
class OutlierReport:
    env_names: List[str]
    entries: List[OutlierEntry] = field(default_factory=list)

    @property
    def has_outliers(self) -> bool:
        return len(self.entries) > 0

    @property
    def outlier_keys(self) -> List[str]:
        return [e.key for e in self.entries]


class OutlierDetector:
    """Identifies keys where one or more environments hold a minority value."""

    def __init__(self, threshold: float = 0.5):
        """
        Args:
            threshold: fraction of envs that must share a value for it to be
                       considered 'common'. Defaults to 0.5 (majority).
        """
        self.threshold = threshold

    def calculate(self, envs: Dict[str, Dict[str, str]]) -> OutlierReport:
        env_names = list(envs.keys())
        all_keys: set = set()
        for env in envs.values():
            all_keys.update(env.keys())

        report = OutlierReport(env_names=env_names)

        for key in sorted(all_keys):
            values = {name: env[key] for name, env in envs.items() if key in env}
            if len(values) < 2:
                continue

            counter = Counter(values.values())
            most_common_value, most_common_count = counter.most_common(1)[0]
            total = len(values)

            if most_common_count / total >= self.threshold:
                # There is a clear majority value — find who differs
                outlier_envs = {
                    env: val
                    for env, val in values.items()
                    if val != most_common_value
                }
                if outlier_envs:
                    report.entries.append(
                        OutlierEntry(
                            key=key,
                            common_value=most_common_value,
                            outlier_envs=outlier_envs,
                        )
                    )
            # If no majority exists, every value is equally valid — skip

        return report
