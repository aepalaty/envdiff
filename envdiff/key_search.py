from dataclasses import dataclass, field
from fnmatch import fnmatch
from typing import Dict, List, Optional


@dataclass
class SearchMatch:
    key: str
    env_name: str
    value: str
    matched_by: str  # 'key', 'value', or 'both'

    def __str__(self) -> str:
        return f"[{self.env_name}] {self.key}={self.value!r} (matched by {self.matched_by})"


@dataclass
class SearchResult:
    query: str
    matches: List[SearchMatch] = field(default_factory=list)

    @property
    def has_matches(self) -> bool:
        return len(self.matches) > 0

    @property
    def matched_envs(self) -> List[str]:
        return sorted(set(m.env_name for m in self.matches))

    @property
    def matched_keys(self) -> List[str]:
        return sorted(set(m.key for m in self.matches))


class KeySearcher:
    def __init__(self, search_keys: bool = True, search_values: bool = False):
        self.search_keys = search_keys
        self.search_values = search_values

    def search(
        self,
        envs: Dict[str, Dict[str, str]],
        query: str,
        glob: bool = False,
    ) -> SearchResult:
        result = SearchResult(query=query)
        for env_name, env in envs.items():
            for key, value in env.items():
                key_hit = self._matches(key, query, glob) if self.search_keys else False
                val_hit = self._matches(value, query, glob) if self.search_values else False
                if key_hit or val_hit:
                    matched_by = "both" if key_hit and val_hit else ("key" if key_hit else "value")
                    result.matches.append(SearchMatch(key=key, env_name=env_name, value=value, matched_by=matched_by))
        return result

    @staticmethod
    def _matches(text: str, query: str, glob: bool) -> bool:
        if glob:
            return fnmatch(text, query)
        return query.lower() in text.lower()
