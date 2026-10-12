"""Solver statistics collected during search."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

from clinicflow.models import Value


@dataclass
class Stats:
    nodes: int = 0  # assignments tried
    backtracks: int = 0  # dead ends (assignment rejected or undone)
    constraint_checks: int = 0  # pairwise consistency checks
    pruned_values: int = 0  # values removed by inference (FC / AC-3)
    runtime_s: float = 0.0

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass
class SolveResult:
    solver: str
    status: str  # "solved" | "infeasible" | "timeout"
    assignment: dict[str, Value] | None
    stats: Stats = field(default_factory=Stats)
    trace: list[str] = field(default_factory=list)

    @property
    def solved(self) -> bool:
        return self.status == "solved"

    def row(self) -> dict:
        return {"solver": self.solver, "status": self.status, **self.stats.as_dict()}
