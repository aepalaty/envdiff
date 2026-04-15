"""Detect keys with leading or trailing whitespace in their values."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class PaddingIssue:
    key: str
    env_name: str
    raw_value: str
    leading: bool
    trailing: bool

    def __str__(self) -> str:
        kinds = []
        if self.leading:
            kinds.append("leading")
        if self.trailing:
            kinds.append("trailing")
        kind_str = " and ".join(kinds)
        return f"{self.key} ({self.env_name}): {kind_str} whitespace in value"


@dataclass
class PaddingReport:
    env_names: List[str]
    issues: List[PaddingIssue] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return len(self.issues) > 0

    @property
    def affected_keys(self) -> List[str]:
        return sorted(set(i.key for i in self.issues))

    def issues_for_env(self, env_name: str) -> List[PaddingIssue]:
        return [i for i in self.issues if i.env_name == env_name]


class PaddingDetector:
    """Scan one or more envs for values with leading/trailing whitespace."""

    def detect(self, envs: Dict[str, Dict[str, str]]) -> PaddingReport:
        env_names = list(envs.keys())
        report = PaddingReport(env_names=env_names)

        for env_name, env in envs.items():
            for key, value in env.items():
                leading = value != value.lstrip()
                trailing = value != value.rstrip()
                if leading or trailing:
                    report.issues.append(
                        PaddingIssue(
                            key=key,
                            env_name=env_name,
                            raw_value=value,
                            leading=leading,
                            trailing=trailing,
                        )
                    )

        return report
