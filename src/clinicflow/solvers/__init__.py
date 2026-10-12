"""Solver registry: the lecture ladder Backtracking -> MRV -> Forward Checking -> AC-3/MAC."""

from __future__ import annotations

from functools import partial

from clinicflow.metrics import SolveResult
from clinicflow.models import Instance
from clinicflow.solvers.backtracking import backtracking_search

SOLVERS = {
    "BT": partial(backtracking_search, ordering="static", inference=None, name="BT"),
    "BT+MRV": partial(backtracking_search, ordering="mrv", inference=None, name="BT+MRV"),
    "BT+FC": partial(backtracking_search, ordering="static", inference="fc", name="BT+FC"),
    "BT+MRV+FC": partial(backtracking_search, ordering="mrv", inference="fc", name="BT+MRV+FC"),
    "BT+MRV+MAC": partial(backtracking_search, ordering="mrv", inference="mac", name="BT+MRV+MAC"),
}


def solve(instance: Instance, solver: str = "BT+MRV+FC", **kwargs) -> SolveResult:
    return SOLVERS[solver](instance, **kwargs)


__all__ = ["SOLVERS", "solve", "backtracking_search"]
