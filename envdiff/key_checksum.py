"""Compute and compare checksums for env file contents to detect silent changes."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ChecksumEntry:
    key: str
    env_name: str
    value_hash: str  # SHA-256 of the value
    value_length: int

    def __str__(self) -> str:
        return f"{self.key} [{self.env_name}]: {self.value_hash[:12]}... (len={self.value_length})"


@dataclass
class ChecksumMismatch:
    key: str
    entries: List[ChecksumEntry] = field(default_factory=list)

    def unique_hashes(self) -> List[str]:
        return list({e.value_hash for e in self.entries})

    def has_mismatch(self) -> bool:
        return len(self.unique_hashes()) > 1

    def __str__(self) -> str:
        envs = ", ".join(e.env_name for e in self.entries)
        return f"{self.key}: {len(self.unique_hashes())} distinct values across [{envs}]"


@dataclass
class ChecksumReport:
    env_names: List[str]
    entries: Dict[str, List[ChecksumEntry]] = field(default_factory=dict)

    def mismatches(self) -> List[ChecksumMismatch]:
        result = []
        for key, ents in self.entries.items():
            m = ChecksumMismatch(key=key, entries=ents)
            if m.has_mismatch():
                result.append(m)
        return result

    def has_mismatches(self) -> bool:
        return any(m.has_mismatch() for m in [
            ChecksumMismatch(key=k, entries=v) for k, v in self.entries.items()
        ])

    def checksum_for(self, key: str, env_name: str) -> Optional[str]:
        for entry in self.entries.get(key, []):
            if entry.env_name == env_name:
                return entry.value_hash
        return None


def _hash_value(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class ChecksumCalculator:
    def calculate(self, envs: Dict[str, Dict[str, str]]) -> ChecksumReport:
        env_names = list(envs.keys())
        all_keys: set = set()
        for env in envs.values():
            all_keys.update(env.keys())

        entries: Dict[str, List[ChecksumEntry]] = {}
        for key in sorted(all_keys):
            key_entries = []
            for env_name, env in envs.items():
                if key in env:
                    value = env[key]
                    key_entries.append(ChecksumEntry(
                        key=key,
                        env_name=env_name,
                        value_hash=_hash_value(value),
                        value_length=len(value),
                    ))
            entries[key] = key_entries

        return ChecksumReport(env_names=env_names, entries=entries)
