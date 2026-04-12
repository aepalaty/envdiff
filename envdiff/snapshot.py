"""Snapshot: capture and persist env state for later diffing."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional


@dataclass
class Snapshot:
    """A point-in-time capture of a parsed .env file."""

    source: str
    captured_at: str
    env: Dict[str, str] = field(default_factory=dict)
    label: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "captured_at": self.captured_at,
            "label": self.label,
            "env": self.env,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Snapshot":
        return cls(
            source=data["source"],
            captured_at=data["captured_at"],
            env=data.get("env", {}),
            label=data.get("label"),
        )


class SnapshotManager:
    """Create, save, and load env snapshots."""

    def __init__(self, snapshot_dir: str = ".envdiff_snapshots") -> None:
        self.snapshot_dir = Path(snapshot_dir)

    def _ensure_dir(self) -> None:
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

    def capture(self, env: Dict[str, str], source: str, label: Optional[str] = None) -> Snapshot:
        """Create a new snapshot from a parsed env dict."""
        now = datetime.now(timezone.utc).isoformat()
        return Snapshot(source=source, captured_at=now, env=dict(env), label=label)

    def save(self, snapshot: Snapshot, filename: Optional[str] = None) -> Path:
        """Persist snapshot to disk as JSON."""
        self._ensure_dir()
        if filename is None:
            ts = snapshot.captured_at.replace(":", "-").replace("+", "Z")
            base = os.path.basename(snapshot.source).replace(".", "_")
            filename = f"{base}_{ts}.json"
        path = self.snapshot_dir / filename
        path.write_text(json.dumps(snapshot.to_dict(), indent=2), encoding="utf-8")
        return path

    def load(self, path: str) -> Snapshot:
        """Load a snapshot from a JSON file.

        Raises:
            FileNotFoundError: If the given path does not exist.
            ValueError: If the file cannot be parsed as valid JSON or is
                missing required fields ('source' or 'captured_at').
        """
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"Snapshot file not found: {path}")
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in snapshot file '{path}': {exc}") from exc
        if "source" not in data or "captured_at" not in data:
            raise ValueError(
                f"Snapshot file '{path}' is missing required fields ('source', 'captured_at')."
            )
        return Snapshot.from_dict(data)

    def list_snapshots(self) -> list[Path]:
        """Return all snapshot files sorted by name."""
        if not self.snapshot_dir.exists():
            return []
        return sorted(self.snapshot_dir.glob("*.json"))
