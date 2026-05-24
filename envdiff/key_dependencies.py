from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class DependencyViolation:
    key: str
    requires: str
    env_name: str

    def __str__(self) -> str:
        return f"{self.env_name}: '{self.key}' requires '{self.requires}' to be present"


@dataclass
class DependencyReport:
    env_names: List[str]
    violations: List[DependencyViolation] = field(default_factory=list)

    @property
    def has_violations(self) -> bool:
        return bool(self.violations)

    def violations_for_env(self, env_name: str) -> List[DependencyViolation]:
        return [v for v in self.violations if v.env_name == env_name]

    def violation_keys(self) -> Set[str]:
        return {v.key for v in self.violations}


class DependencyChecker:
    """
    Checks that when a key is present, all its declared dependencies are also present.
    Dependencies are expressed as a dict: {key: [required_key, ...]}.
    """

    def __init__(self, rules: Dict[str, List[str]]) -> None:
        self.rules = rules

    def calculate(
        self, envs: Dict[str, Dict[str, str]]
    ) -> DependencyReport:
        env_names = list(envs.keys())
        report = DependencyReport(env_names=env_names)

        for env_name, env in envs.items():
            for key, required_keys in self.rules.items():
                if key in env:
                    for req in required_keys:
                        if req not in env:
                            report.violations.append(
                                DependencyViolation(
                                    key=key,
                                    requires=req,
                                    env_name=env_name,
                                )
                            )
        return report
