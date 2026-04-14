from __future__ import annotations

from typing import Optional

from .key_similarity import SimilarityReport


class SimilarityFormatter:
    """Render a SimilarityReport as human-readable text."""

    def __init__(self, color: bool = True, threshold: float = 0.6) -> None:
        self.color = color
        self.threshold = threshold

    def _c(self, text: str, code: str) -> str:
        return f"\033[{code}m{text}\033[0m" if self.color else text

    def _score_color(self, score: float) -> str:
        if score >= 0.85:
            return self._c(f"{score:.2f}", "31")  # red – very similar
        if score >= 0.70:
            return self._c(f"{score:.2f}", "33")  # yellow – moderate
        return self._c(f"{score:.2f}", "36")       # cyan – mild

    def format_report(
        self,
        report: SimilarityReport,
        top_n: Optional[int] = None,
    ) -> str:
        pairs = report.above_threshold(self.threshold)
        if top_n is not None:
            pairs = pairs[:top_n]

        if not pairs:
            return self._c("No suspiciously similar keys found.", "32")

        header = self._c(
            f"Similar key pairs (threshold ≥ {self.threshold:.0%}):", "1"
        )
        lines = [header, ""]
        for pair in pairs:
            score_str = self._score_color(pair.score)
            line = (
                f"  {self._c(pair.key_a, '36')} "
                f"<-> "
                f"{self._c(pair.key_b, '36')}  "
                f"score={score_str}"
            )
            lines.append(line)

        lines.append("")
        lines.append(
            self._c(f"Total similar pairs: {len(pairs)}", "1")
        )
        return "\n".join(lines)
