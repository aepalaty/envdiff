"""Detect potentially exposed secrets by checking for high-entropy values on sensitive keys."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.key_entropy import _shannon_entropy

SENSITIVE_PATTERNS = (
    "SECRET", "PASSWORD", "PASSWD", "TOKEN", "API_KEY", "APIKEY",
    "AUTH", "PRIVATE", "CREDENTIAL", "CERT", "SIGNING",
)

EXPOSED_THRESHOLD = 1.5  # entropy below this on a sensitive key is suspicious
PLACEHOLDER_PATTERNS = ("changeme", "replace_me", "todo", "fixme", "example",
                         "your_", "<", ">", "placeholder", "xxxx")


@dataclass
class SecretIssue:
    key: str
    value: str
    reason: str
    env_name: str

    def __str__(self) -> str:
        masked = self.value[:4] + "****" if len(self.value) > 4 else "****"
        return f"[{self.env_name}] {self.key}={masked!r} — {self.reason}"


@dataclass
class SecretsReport:
    env_names: List[str]
    issues: List[SecretIssue] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return bool(self.issues)

    def issues_for_env(self, env_name: str) -> List[SecretIssue]:
        return [i for i in self.issues if i.env_name == env_name]


def _is_sensitive_key(key: str) -> bool:
    upper = key.upper()
    return any(pat in upper for pat in SENSITIVE_PATTERNS)


def _is_placeholder(value: str) -> bool:
    lower = value.lower()
    return any(p in lower for p in PLACEHOLDER_PATTERNS)


class SecretsChecker:
    """Scan one or more envs for exposed or weak secrets."""

    def __init__(self, entropy_threshold: float = EXPOSED_THRESHOLD):
        self.entropy_threshold = entropy_threshold

    def check(self, envs: Dict[str, Dict[str, str]]) -> SecretsReport:
        report = SecretsReport(env_names=list(envs.keys()))
        for env_name, env in envs.items():
            for key, value in env.items():
                if not _is_sensitive_key(key):
                    continue
                issue = self._evaluate(key, value, env_name)
                if issue:
                    report.issues.append(issue)
        return report

    def _evaluate(self, key: str, value: str, env_name: str) -> Optional[SecretIssue]:
        if not value:
            return SecretIssue(key, value, "sensitive key has empty value", env_name)
        if _is_placeholder(value):
            return SecretIssue(key, value, "value looks like a placeholder", env_name)
        entropy = _shannon_entropy(value)
        if entropy < self.entropy_threshold:
            return SecretIssue(
                key, value,
                f"low entropy ({entropy:.2f}) suggests weak or guessable secret",
                env_name,
            )
        return None
