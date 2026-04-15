"""Format RecommendationReport for terminal output."""

from typing import List

from envdiff.key_recommendations import RecommendationReport, Recommendation

_LEVEL_COLORS = {
    "error": "\033[91m",
    "warning": "\033[93m",
    "info": "\033[94m",
}
_RESET = "\033[0m"
_BOLD = "\033[1m"


class RecommendationsFormatter:
    def __init__(self, color: bool = True):
        self.color = color

    def _c(self, text: str, code: str) -> str:
        return f"{code}{text}{_RESET}" if self.color else text

    def _format_rec(self, rec: Recommendation) -> str:
        color = _LEVEL_COLORS.get(rec.level, "")
        level_tag = self._c(f"[{rec.level.upper()}]", color)
        key_str = self._c(rec.key, _BOLD)
        return f"  {level_tag} {key_str}\n    {rec.message}\n    → {rec.suggestion}"

    def format_report(self, report: RecommendationReport) -> str:
        lines = [self._c(f"Recommendations for: {report.env_name}", _BOLD)]
        if not report.has_recommendations:
            lines.append("  No recommendations — environment looks good.")
            return "\n".join(lines)

        for rec in report.recommendations:
            lines.append(self._format_rec(rec))

        lines.append("")
        lines.append(report.summary())
        return "\n".join(lines)

    def format_all(self, reports: List[RecommendationReport]) -> str:
        if not reports:
            return "No recommendation reports to display."
        sections = [self.format_report(r) for r in reports]
        return "\n\n".join(sections)
