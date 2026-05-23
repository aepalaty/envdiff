from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set


_AUTO_TAGS: Dict[str, List[str]] = {
    "database": ["DB_", "DATABASE_", "POSTGRES_", "MYSQL_", "MONGO_"],
    "auth": ["AUTH_", "JWT_", "OAUTH_", "SESSION_", "TOKEN_"],
    "cache": ["REDIS_", "CACHE_", "MEMCACHE_"],
    "storage": ["S3_", "BUCKET_", "STORAGE_", "GCS_"],
    "email": ["SMTP_", "EMAIL_", "MAIL_", "SENDGRID_"],
    "observability": ["LOG_", "TRACE_", "METRIC_", "SENTRY_", "DATADOG_"],
    "feature": ["FEATURE_", "FLAG_", "FF_"],
}


@dataclass
class TagEntry:
    key: str
    tags: Set[str] = field(default_factory=set)

    def __str__(self) -> str:
        tag_str = ", ".join(sorted(self.tags)) if self.tags else "(none)"
        return f"{self.key}: [{tag_str}]"


@dataclass
class TagReport:
    entries: List[TagEntry] = field(default_factory=list)
    env_name: str = ""

    def keys_for_tag(self, tag: str) -> List[str]:
        return [e.key for e in self.entries if tag in e.tags]

    def tags_for_key(self, key: str) -> Set[str]:
        for entry in self.entries:
            if entry.key == key:
                return entry.tags
        return set()

    def all_tags(self) -> Set[str]:
        result: Set[str] = set()
        for entry in self.entries:
            result.update(entry.tags)
        return result

    def untagged_keys(self) -> List[str]:
        return [e.key for e in self.entries if not e.tags]


class KeyTagger:
    def __init__(self, custom_tags: Dict[str, List[str]] | None = None) -> None:
        self._tags = dict(_AUTO_TAGS)
        if custom_tags:
            for tag, prefixes in custom_tags.items():
                self._tags.setdefault(tag, []).extend(prefixes)

    def _resolve_tags(self, key: str) -> Set[str]:
        upper = key.upper()
        matched: Set[str] = set()
        for tag, prefixes in self._tags.items():
            if any(upper.startswith(p.upper()) for p in prefixes):
                matched.add(tag)
        return matched

    def calculate(self, env: Dict[str, str], env_name: str = "") -> TagReport:
        entries = [
            TagEntry(key=k, tags=self._resolve_tags(k))
            for k in sorted(env.keys())
        ]
        return TagReport(entries=entries, env_name=env_name)
