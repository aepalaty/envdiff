from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FormattingIssue:
    key: str
    env_name: str
    value: str
    issue_type: str  # 'inconsistent_quotes', 'trailing_whitespace', 'mixed_case_value'
    detail: str

    def __str__(self) -> str:
        return f"[{self.env_name}] {self.key}: {self.issue_type} — {self.detail}"


@dataclass
class FormattingReport:
    env_names: List[str]
    issues: List[FormattingIssue] = field(default_factory=list)

    def has_issues(self) -> bool:
        return len(self.issues) > 0

    def issues_for_env(self, env_name: str) -> List[FormattingIssue]:
        return [i for i in self.issues if i.env_name == env_name]

    def issues_for_key(self, key: str) -> List[FormattingIssue]:
        return [i for i in self.issues if i.key == key]

    def issue_types(self) -> List[str]:
        return list({i.issue_type for i in self.issues})


class FormattingChecker:
    def __init__(self, sensitive_patterns: Optional[List[str]] = None):
        self._sensitive = sensitive_patterns or ["password", "secret", "token", "key"]

    def _is_sensitive(self, key: str) -> bool:
        lower = key.lower()
        return any(p in lower for p in self._sensitive)

    def _check_value(self, key: str, value: str, env_name: str) -> List[FormattingIssue]:
        issues = []
        if value != value.strip():
            issues.append(FormattingIssue(
                key=key, env_name=env_name, value=value,
                issue_type="trailing_whitespace",
                detail=f"value has leading/trailing whitespace: {repr(value)}"
            ))
        if value.startswith(("'", '"')) and not value.endswith(value[0]):
            issues.append(FormattingIssue(
                key=key, env_name=env_name, value=value,
                issue_type="inconsistent_quotes",
                detail=f"value has mismatched quotes: {repr(value)}"
            ))
        if not self._is_sensitive(key) and value != value.strip('"').strip("'"):
            raw = value.strip('"').strip("'")
            if raw != value and raw == raw.strip():
                issues.append(FormattingIssue(
                    key=key, env_name=env_name, value=value,
                    issue_type="unnecessary_quotes",
                    detail=f"value is unnecessarily quoted: {repr(value)}"
                ))
        return issues

    def calculate(self, envs: Dict[str, Dict[str, str]]) -> FormattingReport:
        report = FormattingReport(env_names=list(envs.keys()))
        for env_name, env in envs.items():
            for key, value in env.items():
                report.issues.extend(self._check_value(key, value, env_name))
        return report
