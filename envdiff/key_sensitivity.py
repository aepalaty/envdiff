"""Classify keys by sensitivity tier and surface high-risk plain-text values."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re

_CRITICAL_PATTERNS = re.compile(
    r"(secret|private[_-]?key|password|passwd|pwd|token|auth|credential|api[_-]?key|access[_-]?key)",
    re.IGNORECASE,
)
_HIGH_PATTERNS = re.compile(
    r"(cert|ssl|tls|hmac|salt|seed|signing|encryption|cipher)",
    re.IGNORECASE,
)
_MEDIUM_PATTERNS = re.compile(
    r"(url|host|port|endpoint|dsn|connection|database|db[_-]?name|user|username|account)",
    re.IGNORECASE,
)


def _tier(key: str) -> str:
    if _CRITICAL_PATTERNS.search(key):
        return "CRITICAL"
    if _HIGH_PATTERNS.search(key):
        return "HIGH"
    if _MEDIUM_PATTERNS.search(key):
        return "MEDIUM"
    return "LOW"


@dataclass
class SensitivityEntry:
    key: str
    tier: str
    envs_with_plain_value: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        flag = f" [plain in: {', '.join(self.envs_with_plain_value)}]" if self.envs_with_plain_value else ""
        return f"{self.key} ({self.tier}){flag}"


@dataclass
class SensitivityReport:
    entries: List[SensitivityEntry] = field(default_factory=list)
    env_names: List[str] = field(default_factory=list)

    def critical(self) -> List[SensitivityEntry]:
        return [e for e in self.entries if e.tier == "CRITICAL"]

    def high(self) -> List[SensitivityEntry]:
        return [e for e in self.entries if e.tier == "HIGH"]

    def has_plain_secrets(self) -> bool:
        return any(e.envs_with_plain_value for e in self.entries if e.tier in ("CRITICAL", "HIGH"))


_PLACEHOLDER_RE = re.compile(r"^(CHANGE_?ME|REPLACE_?ME|YOUR[_-]|<.+>|\*+|XXXX|PLACEHOLDER|TODO)$", re.IGNORECASE)


def _looks_plain(value: str) -> bool:
    """Return True if the value appears to be a real non-placeholder secret."""
    if not value:
        return False
    if _PLACEHOLDER_RE.match(value.strip()):
        return False
    return True


class SensitivityCalculator:
    def calculate(self, envs: Dict[str, Dict[str, str]]) -> SensitivityReport:
        all_keys: set = set()
        for env in envs.values():
            all_keys.update(env.keys())

        entries: List[SensitivityEntry] = []
        for key in sorted(all_keys):
            tier = _tier(key)
            plain_envs = [
                name for name, env in envs.items()
                if key in env and _looks_plain(env[key])
            ] if tier in ("CRITICAL", "HIGH") else []
            entries.append(SensitivityEntry(key=key, tier=tier, envs_with_plain_value=plain_envs))

        return SensitivityReport(entries=entries, env_names=list(envs.keys()))
