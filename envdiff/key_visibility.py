from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


SENSITIVE_PATTERNS = ("password", "secret", "token", "key", "auth", "credential", "private")
INTERNAL_PATTERNS = ("internal", "debug", "dev", "local", "test", "staging")


def _classify(key: str) -> str:
    lower = key.lower()
    if any(p in lower for p in SENSITIVE_PATTERNS):
        return "private"
    if any(p in lower for p in INTERNAL_PATTERNS):
        return "internal"
    return "public"


@dataclass
class VisibilityEntry:
    key: str
    visibility: str  # 'public', 'internal', 'private'
    envs: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        tag = f"[{self.visibility.upper()}]"
        envs = ", ".join(self.envs)
        return f"{tag} {self.key} ({envs})"


@dataclass
class VisibilityReport:
    entries: List[VisibilityEntry] = field(default_factory=list)
    env_names: List[str] = field(default_factory=list)

    def public_keys(self) -> List[VisibilityEntry]:
        return [e for e in self.entries if e.visibility == "public"]

    def internal_keys(self) -> List[VisibilityEntry]:
        return [e for e in self.entries if e.visibility == "internal"]

    def private_keys(self) -> List[VisibilityEntry]:
        return [e for e in self.entries if e.visibility == "private"]

    def has_private(self) -> bool:
        return bool(self.private_keys())


class VisibilityCalculator:
    def calculate(self, envs: Dict[str, Dict[str, str]]) -> VisibilityReport:
        all_keys: Dict[str, List[str]] = {}
        for env_name, env in envs.items():
            for key in env:
                all_keys.setdefault(key, []).append(env_name)

        entries = [
            VisibilityEntry(key=k, visibility=_classify(k), envs=v)
            for k, v in sorted(all_keys.items())
        ]
        return VisibilityReport(entries=entries, env_names=sorted(envs.keys()))
