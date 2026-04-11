"""Detect and resolve key aliases across .env files.

An alias is when the same logical config value is stored under
different key names in different environments (e.g. DB_URL vs DATABASE_URL).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# Well-known alias groups: any two keys in the same group are considered aliases.
_BUILTIN_ALIAS_GROUPS: List[Tuple[str, ...]] = [
    ("DATABASE_URL", "DB_URL", "DB_CONNECTION"),
    ("SECRET_KEY", "APP_SECRET", "SECRET"),
    ("PORT", "APP_PORT", "SERVER_PORT"),
    ("HOST", "APP_HOST", "SERVER_HOST"),
    ("DEBUG", "APP_DEBUG", "FLASK_DEBUG", "DJANGO_DEBUG"),
    ("LOG_LEVEL", "LOGGING_LEVEL", "APP_LOG_LEVEL"),
    ("REDIS_URL", "REDIS_URI", "CACHE_URL"),
    ("SENTRY_DSN", "SENTRY_URL"),
]


@dataclass
class AliasMatch:
    key_a: str
    key_b: str
    group: Tuple[str, ...]

    def __str__(self) -> str:
        return f"{self.key_a!r} <-> {self.key_b!r} (alias group: {', '.join(self.group)})"


@dataclass
class AliasReport:
    matches: List[AliasMatch] = field(default_factory=list)
    unresolved_a: List[str] = field(default_factory=list)
    unresolved_b: List[str] = field(default_factory=list)

    @property
    def has_aliases(self) -> bool:
        return bool(self.matches)

    def summary(self) -> str:
        lines = []
        if self.matches:
            lines.append(f"Found {len(self.matches)} alias pair(s):")
            for m in self.matches:
                lines.append(f"  {m}")
        else:
            lines.append("No alias pairs detected.")
        return "\n".join(lines)


class KeyAliasDetector:
    """Detect alias relationships between keys in two environments."""

    def __init__(self, extra_groups: Optional[List[Tuple[str, ...]]] = None) -> None:
        self._groups: List[Tuple[str, ...]] = list(_BUILTIN_ALIAS_GROUPS)
        if extra_groups:
            self._groups.extend(extra_groups)

    def _find_group(self, key: str) -> Optional[Tuple[str, ...]]:
        upper = key.upper()
        for group in self._groups:
            if upper in group:
                return group
        return None

    def detect(
        self,
        env_a: Dict[str, str],
        env_b: Dict[str, str],
    ) -> AliasReport:
        """Compare two envs and return alias matches for keys missing in one side."""
        keys_a = set(k.upper() for k in env_a)
        keys_b = set(k.upper() for k in env_b)

        only_in_a = keys_a - keys_b
        only_in_b = keys_b - keys_a

        matches: List[AliasMatch] = []
        matched_a: set = set()
        matched_b: set = set()

        for key_a in only_in_a:
            group = self._find_group(key_a)
            if group is None:
                continue
            for key_b in only_in_b:
                if key_b in group and key_b not in matched_b:
                    matches.append(AliasMatch(key_a=key_a, key_b=key_b, group=group))
                    matched_a.add(key_a)
                    matched_b.add(key_b)
                    break

        return AliasReport(
            matches=matches,
            unresolved_a=sorted(only_in_a - matched_a),
            unresolved_b=sorted(only_in_b - matched_b),
        )
