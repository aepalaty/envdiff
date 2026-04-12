from typing import Optional
from envdiff.key_search import SearchResult


class SearchFormatter:
    def __init__(self, color: bool = True):
        self.color = color

    def _c(self, text: str, code: str) -> str:
        if not self.color:
            return text
        return f"\033[{code}m{text}\033[0m"

    def format_result(self, result: SearchResult) -> str:
        if not result.has_matches:
            return self._c(f"No matches found for '{result.query}'.", "33")

        lines = [
            self._c(f"Search results for '{result.query}':", "1"),
            "",
        ]

        current_env: Optional[str] = None
        for match in sorted(result.matches, key=lambda m: (m.env_name, m.key)):
            if match.env_name != current_env:
                current_env = match.env_name
                lines.append(self._c(f"  [{current_env}]", "36"))
            key_str = self._c(match.key, "32")
            val_str = self._c(repr(match.value), "33")
            by_str = self._c(f"({match.matched_by})", "90")
            lines.append(f"    {key_str} = {val_str}  {by_str}")

        lines.append("")
        total = len(result.matches)
        envs = len(result.matched_envs)
        lines.append(self._c(f"{total} match(es) across {envs} environment(s).", "1"))
        return "\n".join(lines)

    def format_summary(self, result: SearchResult) -> str:
        if not result.has_matches:
            return f"0 matches for '{result.query}'."
        return (
            f"{len(result.matches)} match(es) for '{result.query}' "
            f"in {len(result.matched_envs)} env(s): "
            + ", ".join(result.matched_keys)
        )
