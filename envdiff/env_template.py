"""Generate .env.example / template files from existing env data."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.redactor import Redactor


@dataclass
class TemplateEntry:
    key: str
    placeholder: str
    comment: Optional[str] = None
    required: bool = True

    def render(self) -> str:
        lines = []
        if self.comment:
            lines.append(f"# {self.comment}")
        marker = "" if self.required else "# optional"
        suffix = f"  # {marker}" if marker else ""
        lines.append(f"{self.key}={self.placeholder}{suffix}")
        return "\n".join(lines)


@dataclass
class EnvTemplate:
    entries: List[TemplateEntry] = field(default_factory=list)

    def render(self) -> str:
        return "\n".join(entry.render() for entry in self.entries)


class TemplateGenerator:
    """Builds an EnvTemplate from a parsed env dict."""

    _PLACEHOLDER = "CHANGE_ME"

    def __init__(
        self,
        redactor: Optional[Redactor] = None,
        placeholder: str = _PLACEHOLDER,
        required_keys: Optional[List[str]] = None,
    ) -> None:
        self._redactor = redactor or Redactor()
        self._placeholder = placeholder
        self._required = set(required_keys or [])

    def generate(self, env: Dict[str, str]) -> EnvTemplate:
        entries: List[TemplateEntry] = []
        for key in sorted(env.keys()):
            sensitive = self._redactor.is_sensitive(key)
            placeholder = self._placeholder if sensitive else env[key]
            comment = "sensitive — do not commit real value" if sensitive else None
            required = key in self._required if self._required else True
            entries.append(
                TemplateEntry(
                    key=key,
                    placeholder=placeholder,
                    comment=comment,
                    required=required,
                )
            )
        return EnvTemplate(entries=entries)
