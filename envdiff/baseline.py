"""Baseline management: mark an env file as the reference baseline for future comparisons."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

DEFAULT_BASELINE_FILE = ".envdiff_baseline.json"


@dataclass
class BaselineEntry:
    path: str
    env: Dict[str, str]
    recorded_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    label: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "env": self.env,
            "recorded_at": self.recorded_at,
            "label": self.label,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BaselineEntry":
        return cls(
            path=data["path"],
            env=data["env"],
            recorded_at=data.get("recorded_at", ""),
            label=data.get("label"),
        )


class BaselineManager:
    def __init__(self, store_path: str = DEFAULT_BASELINE_FILE):
        self.store_path = Path(store_path)

    def _load(self) -> Dict[str, dict]:
        if not self.store_path.exists():
            return {}
        with self.store_path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    def _save(self, data: Dict[str, dict]) -> None:
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        with self.store_path.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)

    def record(self, env_path: str, env: Dict[str, str], label: Optional[str] = None) -> BaselineEntry:
        entry = BaselineEntry(path=env_path, env=env, label=label)
        data = self._load()
        data[env_path] = entry.to_dict()
        self._save(data)
        return entry

    def get(self, env_path: str) -> Optional[BaselineEntry]:
        data = self._load()
        if env_path not in data:
            return None
        return BaselineEntry.from_dict(data[env_path])

    def remove(self, env_path: str) -> bool:
        data = self._load()
        if env_path not in data:
            return False
        del data[env_path]
        self._save(data)
        return True

    def list_all(self) -> Dict[str, BaselineEntry]:
        return {k: BaselineEntry.from_dict(v) for k, v in self._load().items()}
