"""Generate actionable recommendations based on diff and analysis results."""

from dataclasses import dataclass, field
from typing import List, Dict

from envdiff.comparator import EnvDifference


@dataclass
class Recommendation:
    level: str  # 'error', 'warning', 'info'
    key: str
    message: str
    suggestion: str

    def __str__(self) -> str:
        return f"[{self.level.upper()}] {self.key}: {self.message} — {self.suggestion}"


@dataclass
class RecommendationReport:
    env_name: str
    recommendations: List[Recommendation] = field(default_factory=list)

    @property
    def has_recommendations(self) -> bool:
        return len(self.recommendations) > 0

    @property
    def errors(self) -> List[Recommendation]:
        return [r for r in self.recommendations if r.level == "error"]

    @property
    def warnings(self) -> List[Recommendation]:
        return [r for r in self.recommendations if r.level == "warning"]

    @property
    def infos(self) -> List[Recommendation]:
        return [r for r in self.recommendations if r.level == "info"]

    def summary(self) -> str:
        return (
            f"{self.env_name}: {len(self.errors)} errors, "
            f"{len(self.warnings)} warnings, {len(self.infos)} info"
        )


class RecommendationEngine:
    """Produces recommendations from an EnvDifference result."""

    SENSITIVE_PATTERNS = ("password", "secret", "token", "key", "auth", "api")

    def generate(self, diff: EnvDifference) -> RecommendationReport:
        report = RecommendationReport(env_name=diff.other_name)

        for key in diff.missing_keys:
            level = "error" if self._is_sensitive(key) else "warning"
            report.recommendations.append(
                Recommendation(
                    level=level,
                    key=key,
                    message=f"Key '{key}' is missing from '{diff.other_name}'",
                    suggestion=f"Add '{key}' to {diff.other_name} based on {diff.baseline_name}",
                )
            )

        for key in diff.extra_keys:
            report.recommendations.append(
                Recommendation(
                    level="info",
                    key=key,
                    message=f"Key '{key}' exists in '{diff.other_name}' but not in baseline",
                    suggestion=f"Verify if '{key}' should be added to {diff.baseline_name} or removed",
                )
            )

        for key, (baseline_val, other_val) in diff.mismatched_keys.items():
            level = "error" if self._is_sensitive(key) else "info"
            report.recommendations.append(
                Recommendation(
                    level=level,
                    key=key,
                    message=f"Value mismatch for '{key}'",
                    suggestion="Review both values and align intentionally or document the difference",
                )
            )

        return report

    def generate_all(self, diffs: List[EnvDifference]) -> List[RecommendationReport]:
        return [self.generate(diff) for diff in diffs]

    def _is_sensitive(self, key: str) -> bool:
        lower = key.lower()
        return any(pat in lower for pat in self.SENSITIVE_PATTERNS)
