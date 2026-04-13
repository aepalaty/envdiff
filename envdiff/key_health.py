"""Key health scoring: assigns a composite health score to each key across environments."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.key_entropy import EntropyReport
from envdiff.key_frequency import FrequencyReport
from envdiff.lint import LintResult


@dataclass
class HealthScore:
    key: str
    score: float  # 0.0 (poor) to 1.0 (excellent)
    reasons: List[str] = field(default_factory=list)

    def grade(self) -> str:
        if self.score >= 0.85:
            return "A"
        elif self.score >= 0.70:
            return "B"
        elif self.score >= 0.50:
            return "C"
        elif self.score >= 0.30:
            return "D"
        return "F"

    def __str__(self) -> str:
        return f"{self.key}: {self.grade()} ({self.score:.2f})"


@dataclass
class HealthReport:
    scores: List[HealthScore] = field(default_factory=list)

    def average_score(self) -> float:
        if not self.scores:
            return 0.0
        return sum(s.score for s in self.scores) / len(self.scores)

    def poor_keys(self, threshold: float = 0.5) -> List[HealthScore]:
        return [s for s in self.scores if s.score < threshold]

    def top_keys(self, n: int = 5) -> List[HealthScore]:
        return sorted(self.scores, key=lambda s: s.score, reverse=True)[:n]


class KeyHealthCalculator:
    """Computes a health score per key using entropy, frequency, and lint signals."""

    def __init__(
        self,
        entropy_report: Optional[EntropyReport] = None,
        frequency_report: Optional[FrequencyReport] = None,
        lint_result: Optional[LintResult] = None,
    ):
        self.entropy_report = entropy_report
        self.frequency_report = frequency_report
        self.lint_result = lint_result

    def calculate(self, all_keys: List[str]) -> HealthReport:
        entropy_map: Dict[str, float] = {}
        if self.entropy_report:
            for entry in self.entropy_report.entries:
                entropy_map[entry.key] = min(entry.entropy / 4.0, 1.0)

        freq_map: Dict[str, float] = {}
        if self.frequency_report:
            total_envs = max(self.frequency_report.total_envs, 1)
            for entry in self.frequency_report.entries:
                freq_map[entry.key] = entry.frequency(total_envs)

        lint_flagged: set = set()
        if self.lint_result:
            for issue in self.lint_result.issues:
                lint_flagged.add(issue.key)

        scores = []
        for key in all_keys:
            reasons = []
            components = []

            entropy_score = entropy_map.get(key, 0.5)
            components.append(entropy_score * 0.4)
            if entropy_score < 0.25:
                reasons.append("low entropy value")

            freq_score = freq_map.get(key, 0.5)
            components.append(freq_score * 0.4)
            if freq_score < 0.5:
                reasons.append("missing in some environments")

            lint_score = 0.0 if key in lint_flagged else 1.0
            components.append(lint_score * 0.2)
            if key in lint_flagged:
                reasons.append("lint issues detected")

            score = sum(components)
            scores.append(HealthScore(key=key, score=round(score, 4), reasons=reasons))

        scores.sort(key=lambda s: s.score)
        return HealthReport(scores=scores)
