"""Detect value mutations for the same key across ordered snapshots."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class MutationEvent:
    snapshot_label: str
    old_value: Optional[str]
    new_value: Optional[str]

    def __str__(self) -> str:
        old = repr(self.old_value) if self.old_value is not None else "<absent>"
        new = repr(self.new_value) if self.new_value is not None else "<absent>"
        return f"[{self.snapshot_label}] {old} -> {new}"


@dataclass
class MutationEntry:
    key: str
    mutations: List[MutationEvent] = field(default_factory=list)

    @property
    def mutation_count(self) -> int:
        return len(self.mutations)

    @property
    def has_mutations(self) -> bool:
        return self.mutation_count > 0

    def __str__(self) -> str:
        return f"{self.key}: {self.mutation_count} mutation(s)"


@dataclass
class MutationReport:
    entries: List[MutationEntry] = field(default_factory=list)

    @property
    def mutated_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.has_mutations]

    @property
    def stable_keys(self) -> List[str]:
        return [e.key for e in self.entries if not e.has_mutations]

    @property
    def total_mutations(self) -> int:
        return sum(e.mutation_count for e in self.entries)


class MutationCalculator:
    """Track value mutations for each key across an ordered list of snapshots."""

    def calculate(
        self, snapshots: List[Tuple[str, Dict[str, str]]]
    ) -> MutationReport:
        """snapshots: list of (label, env_dict) in chronological order."""
        if not snapshots:
            return MutationReport()

        all_keys: set = set()
        for _, env in snapshots:
            all_keys.update(env.keys())

        entries: List[MutationEntry] = []
        for key in sorted(all_keys):
            entry = MutationEntry(key=key)
            prev_value: Optional[str] = None
            prev_label: Optional[str] = None

            for label, env in snapshots:
                current_value = env.get(key)
                if prev_label is not None and current_value != prev_value:
                    entry.mutations.append(
                        MutationEvent(
                            snapshot_label=label,
                            old_value=prev_value,
                            new_value=current_value,
                        )
                    )
                prev_value = current_value
                prev_label = label

            entries.append(entry)

        return MutationReport(entries=entries)
