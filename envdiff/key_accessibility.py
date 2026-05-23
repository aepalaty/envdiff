from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set


_COMMON_REQUIRED = {
    "DATABASE_URL",
    "SECRET_KEY",
    "DEBUG",
    "ALLOWED_HOSTS",
    "PORT",
}


@dataclass
class AccessibilityIssue:
    env_name: str
    key: str
    reason: str

    def __str__(self) -> str:
        return f"[{self.env_name}] {self.key}: {self.reason}"


@dataclass
class AccessibilityReport:
    env_names: List[str]
    issues: List[AccessibilityIssue] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return len(self.issues) > 0

    def issues_for_env(self, env_name: str) -> List[AccessibilityIssue]:
        return [i for i in self.issues if i.env_name == env_name]

    def affected_keys(self) -> Set[str]:
        return {i.key for i in self.issues}


class AccessibilityChecker:
    """Checks whether commonly required keys are accessible (present and non-empty) across envs."""

    def __init__(self, required_keys: Set[str] | None = None) -> None:
        self._required = required_keys if required_keys is not None else _COMMON_REQUIRED

    def calculate(
        self, envs: Dict[str, Dict[str, str]]
    ) -> AccessibilityReport:
        env_names = list(envs.keys())
        report = AccessibilityReport(env_names=env_names)

        for env_name, env in envs.items():
            for key in self._required:
                if key not in env:
                    report.issues.append(
                        AccessibilityIssue(
                            env_name=env_name,
                            key=key,
                            reason="key is missing",
                        )
                    )
                elif env[key].strip() == "":
                    report.issues.append(
                        AccessibilityIssue(
                            env_name=env_name,
                            key=key,
                            reason="key is present but empty",
                        )
                    )

        return report
