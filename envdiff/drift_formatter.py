"""Format DriftReport for terminal output."""
from envdiff.key_drift import DriftReport, DriftEntry


class DriftFormatter:
    def __init__(self, color: bool = True):
        self.color = color

    def _c(self, text: str, code: str) -> str:
        if not self.color:
            return text
        return f"\033[{code}m{text}\033[0m"

    def _format_entry(self, entry: DriftEntry) -> str:
        key_str = self._c(entry.key, "1")
        if not entry.has_drift:
            status = self._c("stable", "32")
            return f"  {key_str}: {status}"
        status = self._c(f"DRIFT ({entry.unique_values} values)", "33")
        lines = [f"  {key_str}: {status}"]
        for env_name, value in zip(entry.env_names, entry.values):
            env_label = self._c(env_name, "36")
            val_label = self._c(repr(value), "35")
            lines.append(f"    {env_label} = {val_label}")
        return "\n".join(lines)

    def format_report(self, report: DriftReport, show_stable: bool = False) -> str:
        lines = [self._c("=== Key Drift Report ===", "1")]

        if not report.entries:
            lines.append("  No keys found.")
            return "\n".join(lines)

        if report.drifted_keys:
            lines.append(self._c("Drifted Keys:", "33"))
            for entry in report.drifted_keys:
                lines.append(self._format_entry(entry))
        else:
            lines.append(self._c("  No drift detected.", "32"))

        if show_stable and report.stable_keys:
            lines.append(self._c("Stable Keys:", "32"))
            for entry in report.stable_keys:
                lines.append(self._format_entry(entry))

        lines.append("")
        lines.append(self._c(report.summary, "1"))
        return "\n".join(lines)
