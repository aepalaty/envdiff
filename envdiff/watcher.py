"""File watcher for monitoring .env file changes and reporting diffs in real time."""

import time
import os
from pathlib import Path
from typing import Callable, Dict, List, Optional

from envdiff.parser import parse_file
from envdiff.comparator import EnvComparator
from envdiff.formatter import DiffFormatter


class WatchedFile:
    """Tracks the state of a single .env file on disk."""

    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self._last_mtime: Optional[float] = None
        self._last_env: Dict[str, str] = {}

    def has_changed(self) -> bool:
        """Return True if the file has been modified since last check."""
        try:
            mtime = self.path.stat().st_mtime
        except FileNotFoundError:
            return False
        if self._last_mtime is None or mtime != self._last_mtime:
            self._last_mtime = mtime
            return True
        return False

    def read(self) -> Dict[str, str]:
        """Parse and return the current env contents, caching the result."""
        self._last_env = parse_file(str(self.path))
        return self._last_env

    @property
    def cached_env(self) -> Dict[str, str]:
        """Return the last successfully parsed env dict."""
        return self._last_env


class EnvWatcher:
    """Watch a baseline .env file and one or more comparison files for changes.

    When any file changes, a fresh diff is computed and the provided callback
    is invoked with the formatted output.
    """

    def __init__(
        self,
        baseline: str,
        others: List[str],
        callback: Optional[Callable[[str], None]] = None,
        poll_interval: float = 1.0,
        color: bool = True,
    ) -> None:
        """
        Args:
            baseline: Path to the baseline .env file.
            others: Paths to the other .env files to compare against.
            callback: Function called with the formatted diff string whenever
                      a change is detected.  Defaults to printing to stdout.
            poll_interval: Seconds between filesystem polls.
            color: Whether to enable ANSI colour in formatter output.
        """
        self._baseline = WatchedFile(baseline)
        self._others = [WatchedFile(p) for p in others]
        self._callback = callback or print
        self._poll_interval = poll_interval
        self._formatter = DiffFormatter(color=color)
        self._running = False

        # Prime the initial state so the first iteration doesn't always fire.
        self._baseline.has_changed()
        self._baseline.read()
        for wf in self._others:
            wf.has_changed()
            wf.read()

    def _check_and_report(self) -> None:
        """Check all watched files; emit a diff report if anything changed."""
        changed = self._baseline.has_changed()
        for wf in self._others:
            if wf.has_changed():
                changed = True

        if not changed:
            return

        baseline_env = self._baseline.read()
        lines: List[str] = []

        for wf in self._others:
            other_env = wf.read()
            comparator = EnvComparator(baseline_env, other_env)
            diff = comparator.compare()
            header = (
                f"--- {self._baseline.path.name}  "
                f"+++ {wf.path.name}"
            )
            lines.append(header)
            lines.append(self._formatter.format_difference(diff))
            lines.append(self._formatter.format_summary(diff))
            lines.append("")

        self._callback("\n".join(lines).rstrip())

    def run_once(self) -> None:
        """Perform a single poll cycle (useful for testing)."""
        self._check_and_report()

    def start(self) -> None:
        """Block and poll indefinitely until :meth:`stop` is called."""
        self._running = True
        try:
            while self._running:
                self._check_and_report()
                time.sleep(self._poll_interval)
        except KeyboardInterrupt:
            self._running = False

    def stop(self) -> None:
        """Signal the watch loop to exit after the current iteration."""
        self._running = False
