from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


DEFAULT_MAX_LENGTH = 256


@dataclass
class TruncationIssue:
    env_name: str
    key: str
    value_length: int
    max_length: int

    def __str__(self) -> str:
        return (
            f"{self.key} in [{self.env_name}]: "
            f"value length {self.value_length} exceeds max {self.max_length}"
        )


@dataclass
class TruncationReport:
    env_names: List[str]
    issues: List[TruncationIssue] = field(default_factory=list)

    def has_issues(self) -> bool:
        return len(self.issues) > 0

    def issues_for_env(self, env_name: str) -> List[TruncationIssue]:
        return [i for i in self.issues if i.env_name == env_name]

    def affected_keys(self) -> List[str]:
        return sorted({i.key for i in self.issues})


class TruncationChecker:
    def __init__(self, max_length: int = DEFAULT_MAX_LENGTH) -> None:
        self.max_length = max_length

    def check(
        self, envs: Dict[str, Dict[str, str]]
    ) -> TruncationReport:
        env_names = list(envs.keys())
        report = TruncationReport(env_names=env_names)

        for env_name, env in envs.items():
            for key, value in env.items():
                if value is None:
                    continue
                if len(value) > self.max_length:
                    report.issues.append(
                        TruncationIssue(
                            env_name=env_name,
                            key=key,
                            value_length=len(value),
                            max_length=self.max_length,
                        )
                    )

        return report
