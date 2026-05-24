from __future__ import annotations
from typing import Optional
from .key_compression import CompressionReport


class CompressionFormatter:
    def __init__(self, color: bool = True):
        self._color = color

    def _c(self, text: str, code: str) -> str:
        if not self._color:
            return text
        return f"\033[{code}m{text}\033[0m"

    def _ratio_color(self, ratio: float) -> str:
        if ratio < 0.5:
            return self._c(f"{ratio:.1%}", "32")  # green
        if ratio < 0.8:
            return self._c(f"{ratio:.1%}", "33")  # yellow
        return self._c(f"{ratio:.1%}", "31")  # red

    def _format_bar(self, ratio: float, width: int = 20) -> str:
        filled = max(0, min(width, int((1.0 - ratio) * width)))
        bar = "#" * filled + "-" * (width - filled)
        return f"[{bar}]"

    def format_report(
        self, report: CompressionReport, top_n: Optional[int] = None
    ) -> str:
        lines = [self._c("Key Compression Analysis", "1"), ""]
        lines.append(
            f"Environments : {', '.join(report.env_names)}"
        )
        lines.append(
            f"Average ratio: {self._ratio_color(report.average_ratio)}"
        )
        compressible = report.compressible_keys
        lines.append(
            f"Compressible keys: {self._c(str(len(compressible)), '33')}"
        )
        lines.append("")

        entries = sorted(report.entries, key=lambda e: e.ratio)
        if top_n is not None:
            entries = entries[:top_n]

        if not entries:
            lines.append(self._c("No entries to display.", "90"))
            return "\n".join(lines)

        header = f"  {'KEY':<30} {'ORIG':>6} {'COMP':>6} {'RATIO':>7}  BAR"
        lines.append(header)
        lines.append("-" * 65)
        for entry in entries:
            bar = self._format_bar(entry.ratio)
            ratio_str = self._ratio_color(entry.ratio)
            lines.append(
                f"  {entry.key:<30} {entry.original_size:>6} "
                f"{entry.compressed_size:>6} {ratio_str:>7}  {bar}"
            )

        return "\n".join(lines)
