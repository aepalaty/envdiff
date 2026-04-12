"""Format KeyAnnotator reports for CLI display."""
from typing import List
from envdiff.key_annotator import AnnotationReport, KeyAnnotation


class AnnotationFormatter:
    def __init__(self, use_color: bool = True):
        self.use_color = use_color

    def _c(self, text: str, code: str) -> str:
        if not self.use_color:
            return text
        return f"\033[{code}m{text}\033[0m"

    def _format_annotation(self, ann: KeyAnnotation) -> str:
        key_str = self._c(ann.key, "36")
        if ann.has_value:
            status = self._c("set", "32")
        else:
            status = self._c("empty", "33")
        line_ref = self._c(f"line {ann.line_number}", "90")
        return f"  {key_str:<40} {status:<12} {line_ref}"

    def format_report(self, report: AnnotationReport) -> str:
        lines: List[str] = []
        header = self._c(f"Annotations for: {report.env_name}", "1")
        lines.append(header)
        lines.append(self._c(f"  Total keys : {report.total_keys}", "0"))
        lines.append(self._c(f"  Populated  : {len(report.populated_keys)}", "32"))
        lines.append(self._c(f"  Empty      : {len(report.empty_keys)}", "33"))
        lines.append("")
        if not report.annotations:
            lines.append(self._c("  (no keys found)", "90"))
        else:
            col_header = f"  {'KEY':<40} {'STATUS':<12} LOCATION"
            lines.append(self._c(col_header, "90"))
            lines.append(self._c("  " + "-" * 60, "90"))
            for ann in report.annotations:
                lines.append(self._format_annotation(ann))
        return "\n".join(lines)

    def format_summary(self, reports: List[AnnotationReport]) -> str:
        lines: List[str] = []
        for report in reports:
            lines.append(self.format_report(report))
            lines.append("")
        return "\n".join(lines).rstrip()
