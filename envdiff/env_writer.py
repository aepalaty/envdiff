"""Write merged or patched env data back to .env file format."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional


class EnvWriter:
    """Renders and writes a dictionary of env key-value pairs to .env format."""

    def __init__(self, indent_exports: bool = False, sort_keys: bool = False):
        self.indent_exports = indent_exports
        self.sort_keys = sort_keys

    def render(self, env: Dict[str, str], header: Optional[str] = None) -> str:
        """Render env dict to .env file content string."""
        lines: List[str] = []

        if header:
            for line in header.strip().splitlines():
                lines.append(f"# {line}" if not line.startswith("#") else line)
            lines.append("")

        keys = sorted(env.keys()) if self.sort_keys else list(env.keys())

        for key in keys:
            value = env[key]
            formatted_value = self._format_value(value)
            if self.indent_exports:
                lines.append(f"export {key}={formatted_value}")
            else:
                lines.append(f"{key}={formatted_value}")

        lines.append("")  # trailing newline
        return "\n".join(lines)

    def _format_value(self, value: str) -> str:
        """Quote value if it contains spaces, special chars, or is empty."""
        if not value:
            return "\"\""
        needs_quotes = any(c in value for c in (" ", "\t", "#", "$", "'", '"', "\\"))
        if needs_quotes:
            escaped = value.replace("\\", "\\\\").replace('"', '\\"')
            return f'"{escaped}"'
        return value

    def write(self, env: Dict[str, str], path: Path, header: Optional[str] = None) -> None:
        """Write rendered env content to the given file path."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        content = self.render(env, header=header)
        path.write_text(content, encoding="utf-8")

    @staticmethod
    def default_filename() -> str:
        return ".env.merged"
