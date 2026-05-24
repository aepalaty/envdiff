from typing import Optional
from envdiff.key_provenance import ProvenanceReport


class ProvenanceFormatter:
    def __init__(self, color: bool = True):
        self._color = color

    def _c(self, text: str, code: str) -> str:
        if not self._color:
            return text
        return f"\033[{code}m{text}\033[0m"

    def _format_entry_row(self, entry) -> str:
        key_str = self._c(entry.key, "36")
        src_count = len(entry.sources)
        sources_str = ", ".join(entry.sources)
        if entry.value_consistent:
            status = self._c("consistent", "32")
        else:
            status = self._c("inconsistent", "31")
        return f"  {key_str}  [{src_count} source(s): {sources_str}]  {status}"

    def format_report(self, report: ProvenanceReport) -> str:
        lines = []
        header = self._c("Key Provenance Report", "1;34")
        lines.append(header)
        lines.append(f"Environments: {', '.join(report.env_names)}")
        lines.append("")

        if not report.entries:
            lines.append(self._c("  No keys found.", "33"))
            return "\n".join(lines)

        for entry in report.entries:
            lines.append(self._format_entry_row(entry))

        lines.append("")
        inconsistent = report.inconsistent_keys()
        single = report.keys_from_single_source()
        lines.append(
            f"Summary: {len(report.entries)} keys, "
            f"{len(inconsistent)} inconsistent, "
            f"{len(single)} single-source"
        )
        return "\n".join(lines)

    def format_summary(self, report: ProvenanceReport) -> str:
        inc = len(report.inconsistent_keys())
        if inc == 0:
            return self._c("All keys are consistent across sources.", "32")
        return self._c(f"{inc} key(s) have inconsistent values across sources.", "31")
