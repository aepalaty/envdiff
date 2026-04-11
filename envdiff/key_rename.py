"""Detect and suggest key renames between two environments."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher


@dataclass
class RenameCandidate:
    old_key: str
    new_key: str
    score: float
    value_match: bool

    def __str__(self) -> str:
        match_note = " (value match)" if self.value_match else ""
        return f"{self.old_key!r} -> {self.new_key!r} (score={self.score:.2f}{match_note})"


@dataclass
class RenameReport:
    candidates: List[RenameCandidate] = field(default_factory=list)
    unmatched_old: List[str] = field(default_factory=list)
    unmatched_new: List[str] = field(default_factory=list)

    def has_candidates(self) -> bool:
        return len(self.candidates) > 0


class KeyRenameDetector:
    def __init__(self, threshold: float = 0.6, prefer_value_match: bool = True):
        self.threshold = threshold
        self.prefer_value_match = prefer_value_match

    def _similarity(self, a: str, b: str) -> float:
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def detect(
        self,
        old_env: Dict[str, str],
        new_env: Dict[str, str],
        missing_keys: List[str],
        extra_keys: List[str],
    ) -> RenameReport:
        candidates: List[RenameCandidate] = []
        matched_old = set()
        matched_new = set()

        pairs: List[Tuple[str, str, float, bool]] = []
        for old_key in missing_keys:
            for new_key in extra_keys:
                score = self._similarity(old_key, new_key)
                value_match = old_env.get(old_key) == new_env.get(new_key)
                if self.prefer_value_match and value_match:
                    score = min(1.0, score + 0.2)
                if score >= self.threshold:
                    pairs.append((old_key, new_key, score, value_match))

        pairs.sort(key=lambda x: x[2], reverse=True)

        for old_key, new_key, score, value_match in pairs:
            if old_key not in matched_old and new_key not in matched_new:
                candidates.append(RenameCandidate(old_key, new_key, score, value_match))
                matched_old.add(old_key)
                matched_new.add(new_key)

        unmatched_old = [k for k in missing_keys if k not in matched_old]
        unmatched_new = [k for k in extra_keys if k not in matched_new]

        return RenameReport(
            candidates=candidates,
            unmatched_old=unmatched_old,
            unmatched_new=unmatched_new,
        )
