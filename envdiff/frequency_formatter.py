from typing import Optional
from envdiff.key_frequency import FrequencyReport, FrequencyEntry


class FrequencyFormatter:
    def __init__(self, color: bool = True):
        self.color = color

    def _c(self, text: str, code: str) -> str:
        if not self.color:
            return text
        return f"\033[{code}m{text}\033[0m"

    def _format_bar(self, count: int, total: int, width: int = 20) -> str:
        filled = int((count / max(total, 1)) * width)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"

    def _format_entry(self, entry: FrequencyEntry, total_envs: int) -> str:
        pct = int((entry.count / max(total_envs, 1)) * 100)
        bar = self._format_bar(entry.count, total_envs)
        key_str = self._c(entry.key, "36")
        count_str = self._c(f"{entry.count}/{total_envs}", "33")
        pct_str = self._c(f"{pct:3d}%", "32" if pct == 100 else "33" if pct >= 50 else "31")
        return f"  {key_str:<40} {bar} {count_str}  {pct_str}"

    def format_report(self, report: FrequencyReport, top: int = 20) -> str:
        lines = []
        header = self._c("Key Frequency Report", "1;37")
        lines.append(header)
        lines.append(self._c(f"Environments: {report.total_envs}", "90"))
        lines.append("")

        lines.append(self._c(f"Top {min(top, len(report.entries))} Keys by Frequency:", "1;34"))
        for entry in report.most_common(top):
            lines.append(self._format_entry(entry, report.total_envs))

        universal = report.universal_keys()
        unique = report.unique_keys()
        lines.append("")
        lines.append(self._c(f"Universal keys (in all envs): {len(universal)}", "32"))
        lines.append(self._c(f"Unique keys (in only 1 env):  {len(unique)}", "31"))

        return "\n".join(lines)

    def format_summary(self, report: FrequencyReport) -> str:
        total = len(report.entries)
        universal = len(report.universal_keys())
        unique = len(report.unique_keys())
        return (
            f"{total} total keys | "
            f"{universal} universal | "
            f"{unique} unique to one env"
        )
