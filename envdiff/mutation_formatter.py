"""Format MutationReport for terminal output."""
from typing import Optional

from envdiff.key_mutations import MutationEntry, MutationReport


class MutationFormatter:
    def __init__(self, color: bool = True):
        self._color = color

    def _c(self, text: str, code: str) -> str:
        if not self._color:
            return text
        return f"\033[{code}m{text}\033[0m"

    def _format_entry(self, entry: MutationEntry) -> str:
        lines = []
        key_label = self._c(entry.key, "1;36")
        if not entry.has_mutations:
            lines.append(f"  {key_label}  {self._c('stable', '32')}")
            return "\n".join(lines)

        count_label = self._c(str(entry.mutation_count), "33")
        lines.append(f"  {key_label}  {count_label} mutation(s)")
        for event in entry.mutations:
            old = (
                self._c(repr(event.old_value), "31")
                if event.old_value is not None
                else self._c("<absent>", "90")
            )
            new = (
                self._c(repr(event.new_value), "32")
                if event.new_value is not None
                else self._c("<absent>", "90")
            )
            snap = self._c(f"[{event.snapshot_label}]", "90")
            lines.append(f"    {snap} {old} -> {new}")
        return "\n".join(lines)

    def format_report(self, report: MutationReport) -> str:
        if not report.entries:
            return self._c("No snapshot data to analyse.", "90")

        sections = [
            self._c("=== Key Mutation Report ===", "1"),
        ]
        for entry in report.entries:
            sections.append(self._format_entry(entry))

        sections.append(self.format_summary(report))
        return "\n".join(sections)

    def format_summary(self, report: MutationReport) -> str:
        mutated = len(report.mutated_keys)
        stable = len(report.stable_keys)
        total = report.total_mutations
        parts = [
            self._c("Summary:", "1"),
            f"  Mutated keys : {self._c(str(mutated), '33')}",
            f"  Stable keys  : {self._c(str(stable), '32')}",
            f"  Total changes: {self._c(str(total), '33')}",
        ]
        return "\n".join(parts)
