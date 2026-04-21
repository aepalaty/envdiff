"""Detect keys or values that exceed configurable length thresholds."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


DEFAULT_MAX_KEY_LENGTH = 64
DEFAULT_MAX_VALUE_LENGTH = 512


@dataclass
class LengthIssue:
    env_name: str
    key: str
    kind: str          # 'key' or 'value'
    length: int
    limit: int

    def __str__(self) -> str:
        return (
            f"[{self.env_name}] {self.kind.upper()} '{self.key}' "
            f"length {self.length} exceeds limit {self.limit}"
        )


@dataclass
class LengthReport:
    env_names: List[str]
    issues: List[LengthIssue] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return bool(self.issues)

    def issues_for_env(self, env_name: str) -> List[LengthIssue]:
        return [i for i in self.issues if i.env_name == env_name]

    def affected_keys(self) -> List[str]:
        return sorted({i.key for i in self.issues})


class KeyLengthChecker:
    def __init__(
        self,
        max_key_length: int = DEFAULT_MAX_KEY_LENGTH,
        max_value_length: int = DEFAULT_MAX_VALUE_LENGTH,
    ) -> None:
        self.max_key_length = max_key_length
        self.max_value_length = max_value_length

    def check(
        self, envs: Dict[str, Dict[str, str]]
    ) -> LengthReport:
        env_names = list(envs.keys())
        report = LengthReport(env_names=env_names)

        for env_name, env in envs.items():
            for key, value in env.items():
                if len(key) > self.max_key_length:
                    report.issues.append(
                        LengthIssue(
                            env_name=env_name,
                            key=key,
                            kind="key",
                            length=len(key),
                            limit=self.max_key_length,
                        )
                    )
                if len(value) > self.max_value_length:
                    report.issues.append(
                        LengthIssue(
                            env_name=env_name,
                            key=key,
                            kind="value",
                            length=len(value),
                            limit=self.max_value_length,
                        )
                    )
        return report
