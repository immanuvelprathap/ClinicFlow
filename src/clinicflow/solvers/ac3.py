"""AC-3 arc consistency (Lecture 04, constraint propagation)."""

from __future__ import annotations

from collections import deque

from clinicflow.csp import Domains, conflicts
from clinicflow.metrics import Stats
from clinicflow.models import Instance


def revise(instance: Instance, domains: Domains, xi: str, xj: str, stats: Stats) -> bool:
    """Remove values of xi that have no supporting value in xj. Return True if changed."""
    a = instance_appt(instance, xi)
    b = instance_appt(instance, xj)
    keep = []
    for va in domains[xi]:
        supported = False
        for vb in domains[xj]:
            stats.constraint_checks += 1
            if not conflicts(a, va, b, vb):
                supported = True
                break
        if supported:
            keep.append(va)
    removed = len(domains[xi]) - len(keep)
    if removed:
        stats.pruned_values += removed
        domains[xi] = keep
        return True
    return False


def instance_appt(instance: Instance, appt_id: str):
    for a in instance.appointments:
        if a.id == appt_id:
            return a
    raise KeyError(appt_id)


def ac3(instance: Instance, domains: Domains, stats: Stats, variables: list[str] | None = None,
        start_arcs: list[tuple[str, str]] | None = None) -> bool:
    """Enforce arc consistency in place. Return False if a domain is wiped out."""
    variables = variables if variables is not None else list(domains)
    if start_arcs is None:
        queue = deque((xi, xj) for xi in variables for xj in variables if xi != xj)
    else:
        queue = deque(start_arcs)
    while queue:
        xi, xj = queue.popleft()
        if revise(instance, domains, xi, xj, stats):
            if not domains[xi]:
                return False
            for xk in variables:
                if xk != xi and xk != xj:
                    queue.append((xk, xi))
    return True
