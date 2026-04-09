"""Write a MergeResult to a .env file, optionally annotating conflicts."""

from pathlib import Path
from typing import Optional

from envdiff.merger import MergeResult


class MergeWriter:
    """Serialises a MergeResult back to .env format."""

    def __init__(self, annotate_conflicts: bool = True):
        self.annotate_conflicts = annotate_conflicts

    def render(self, result: MergeResult) -> str:
        """Return the merged env content as a string."""
        conflict_keys = set(result.conflict_keys())
        lines = []

        if result.sources:
            sources_str = ", ".join(result.sources)
            lines.append(f"# Merged from: {sources_str}")
            lines.append("")

        for key, value in sorted(result.merged.items()):
            if self.annotate_conflicts and key in conflict_keys:
                conflict = next(c for c in result.conflicts if c.key == key)
                lines.append(f"# CONFLICT: {conflict}")
            lines.append(f"{key}={value}")

        return "\n".join(lines) + "\n"

    def write(self, result: MergeResult, path: str | Path) -> Path:
        """Write the merged result to *path*, creating parent dirs as needed."""
        dest = Path(path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(self.render(result), encoding="utf-8")
        return dest

    @staticmethod
    def default_filename(sources: list[str]) -> str:
        """Suggest a filename based on the source labels."""
        if not sources:
            return "merged.env"
        slug = "_".join(s.replace(" ", "-") for s in sources)
        return f"merged_{slug}.env"
