from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class WhitespaceIssue:
    env_name: str
    key: str
    value: str
    leading: bool
    trailing: bool
    internal: bool

    def __str__(self) -> str:
        kinds = []
        if self.leading:
            kinds.append("leading")
        if self.trailing:
            kinds.append("trailing")
        if self.internal:
            kinds.append("internal")
        return f"{self.key} [{self.env_name}]: {', '.join(kinds)} whitespace"


@dataclass
class WhitespaceReport:
    env_names: List[str]
    issues: List[WhitespaceIssue] = field(default_factory=list)

    def has_issues(self) -> bool:
        return len(self.issues) > 0

    def issues_for_env(self, env_name: str) -> List[WhitespaceIssue]:
        return [i for i in self.issues if i.env_name == env_name]

    def affected_keys(self) -> List[str]:
        return sorted(set(i.key for i in self.issues))


class WhitespaceChecker:
    def calculate(self, envs: Dict[str, Dict[str, str]]) -> WhitespaceReport:
        report = WhitespaceReport(env_names=list(envs.keys()))
        for env_name, env in envs.items():
            for key, value in env.items():
                leading = value != value.lstrip(" \t")
                trailing = value != value.rstrip(" \t")
                stripped = value.strip()
                internal = "  " in stripped or "\t" in stripped
                if leading or trailing or internal:
                    report.issues.append(
                        WhitespaceIssue(
                            env_name=env_name,
                            key=key,
                            value=value,
                            leading=leading,
                            trailing=trailing,
                            internal=internal,
                        )
                    )
        return report
