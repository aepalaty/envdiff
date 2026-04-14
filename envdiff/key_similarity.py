from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import math


def _ngrams(text: str, n: int = 2) -> set:
    text = text.lower()
    return {text[i:i+n] for i in range(len(text) - n + 1)}


def _dice_coefficient(a: str, b: str, n: int = 2) -> float:
    """Compute Sørensen–Dice coefficient between two strings using n-grams."""
    if a == b:
        return 1.0
    if len(a) < n or len(b) < n:
        return 0.0
    set_a = _ngrams(a, n)
    set_b = _ngrams(b, n)
    intersection = len(set_a & set_b)
    return (2 * intersection) / (len(set_a) + len(set_b))


@dataclass
class SimilarityPair:
    key_a: str
    key_b: str
    score: float  # 0.0 – 1.0

    def __str__(self) -> str:
        return f"{self.key_a} <-> {self.key_b}  ({self.score:.2f})"


@dataclass
class SimilarityReport:
    pairs: List[SimilarityPair] = field(default_factory=list)

    @property
    def has_similar(self) -> bool:
        return len(self.pairs) > 0

    def above_threshold(self, threshold: float = 0.6) -> List[SimilarityPair]:
        return [p for p in self.pairs if p.score >= threshold]

    def top(self, n: int = 10) -> List[SimilarityPair]:
        return sorted(self.pairs, key=lambda p: p.score, reverse=True)[:n]


class KeySimilarityCalculator:
    """Detect suspiciously similar key names across one or more envs."""

    def __init__(self, threshold: float = 0.6, ngram_size: int = 2) -> None:
        self.threshold = threshold
        self.ngram_size = ngram_size

    def calculate(self, envs: Dict[str, Dict[str, str]]) -> SimilarityReport:
        """Compare all unique keys across *envs* and return similar pairs."""
        all_keys: List[str] = sorted(
            {k for env in envs.values() for k in env}
        )
        pairs: List[SimilarityPair] = []
        for i, key_a in enumerate(all_keys):
            for key_b in all_keys[i + 1:]:
                score = _dice_coefficient(key_a, key_b, self.ngram_size)
                if score >= self.threshold:
                    pairs.append(SimilarityPair(key_a, key_b, round(score, 4)))
        pairs.sort(key=lambda p: p.score, reverse=True)
        return SimilarityReport(pairs=pairs)
