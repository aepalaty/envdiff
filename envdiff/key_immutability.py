from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ImmutabilityIssue:
    key: str
    env_name: str
    old_value: str
    new_value: str
    snapshot_label: str

    def __str__(self) -> str:
        return (
            f"{self.key} changed in '{self.env_name}' "
            f"(snapshot: {self.snapshot_label}): "
            f"'{self.old_value}' -> '{self.new_value}'"
        )


@dataclass
class ImmutabilityReport:
    env_names: List[str]
    issues: List[ImmutabilityIssue] = field(default_factory=list)

    def has_issues(self) -> bool:
        return len(self.issues) > 0

    def issues_for_key(self, key: str) -> List[ImmutabilityIssue]:
        return [i for i in self.issues if i.key == key]

    def issues_for_env(self, env_name: str) -> List[ImmutabilityIssue]:
        return [i for i in self.issues if i.env_name == env_name]

    def affected_keys(self) -> List[str]:
        return sorted(set(i.key for i in self.issues))


class ImmutabilityChecker:
    """Detects keys that changed value across snapshots, flagging them as
    potentially violating an immutability contract (e.g. APP_VERSION, ENV_NAME)."""

    def __init__(self, pinned_keys: Optional[List[str]] = None):
        self.pinned_keys = set(pinned_keys) if pinned_keys else set()

    def calculate(
        self,
        snapshots: List[Dict[str, Dict[str, str]]],
        labels: Optional[List[str]] = None,
    ) -> ImmutabilityReport:
        """snapshots: list of {env_name: {key: value}} dicts ordered by time."""
        if not snapshots:
            return ImmutabilityReport(env_names=[])

        env_names = sorted(
            {env for snap in snapshots for env in snap}
        )
        if labels is None:
            labels = [f"snap_{i}" for i in range(len(snapshots))]

        issues: List[ImmutabilityIssue] = []

        for env in env_names:
            prev_values: Dict[str, str] = {}
            for snap, label in zip(snapshots, labels):
                env_data = snap.get(env, {})
                for key, value in env_data.items():
                    if key not in self.pinned_keys:
                        continue
                    if key in prev_values and prev_values[key] != value:
                        issues.append(
                            ImmutabilityIssue(
                                key=key,
                                env_name=env,
                                old_value=prev_values[key],
                                new_value=value,
                                snapshot_label=label,
                            )
                        )
                    prev_values[key] = value

        return ImmutabilityReport(env_names=env_names, issues=issues)
