"""Configurable backtracking search (Lecture 04).

One engine, three switches, so the comparison is apples-to-apples:
  variable ordering : "static" (input order)  | "mrv" (fewest legal values, degree tie-break)
  inference         : None | "fc" (forward checking) | "mac" (AC-3 after each assignment)
"""

from __future__ import annotations

import time

from clinicflow.csp import Assignment, Domains, build_domains, conflicts
from clinicflow.metrics import SolveResult, Stats
from clinicflow.models import Instance
from clinicflow.solvers.ac3 import ac3


class Timeout(Exception):
    pass


def backtracking_search(
    instance: Instance,
    *,
    ordering: str = "static",
    inference: str | None = None,
    name: str = "BT",
    time_limit_s: float | None = None,
    keep_trace: bool = False,
) -> SolveResult:
    stats = Stats()
    trace: list[str] = []
    appts = {a.id: a for a in instance.appointments}
    order = [a.id for a in instance.appointments]
    domains = build_domains(instance)
    t0 = time.perf_counter()
    deadline = t0 + time_limit_s if time_limit_s else None

    def log(msg: str) -> None:
        if keep_trace and len(trace) < 5000:
            trace.append(msg)

    def select_variable(assignment: Assignment, doms: Domains) -> str:
        unassigned = [v for v in order if v not in assignment]
        if ordering == "mrv":
            # MRV: fewest remaining values; degree heuristic as tie-break
            # (all pairs can clash, so degree == number of unassigned others; tie-break on input order).
            return min(unassigned, key=lambda v: (len(doms[v]), order.index(v)))
        return unassigned[0]

    def consistent(var: str, value, assignment: Assignment) -> bool:
        for other, ov in assignment.items():
            stats.constraint_checks += 1
            if conflicts(appts[var], value, appts[other], ov):
                return False
        return True

    def infer(var: str, value, assignment: Assignment, doms: Domains) -> Domains | None:
        """Return pruned copy of domains, or None on wipe-out."""
        new = {k: (v if k in assignment or k == var else list(v)) for k, v in doms.items()}
        new[var] = [value]
        if inference in ("fc", "mac"):
            for other in new:
                if other in assignment or other == var:
                    continue
                kept = []
                for ov in new[other]:
                    stats.constraint_checks += 1
                    if not conflicts(appts[var], value, appts[other], ov):
                        kept.append(ov)
                stats.pruned_values += len(new[other]) - len(kept)
                new[other] = kept
                if not kept:
                    log(f"  FC wipe-out: {other} has no values left")
                    return None
        if inference == "mac":
            unassigned = [v for v in order if v not in assignment and v != var]
            arcs = [(xk, var) for xk in unassigned]
            if not ac3(instance, new, stats, variables=unassigned + [var], start_arcs=arcs):
                log("  AC-3 wipe-out")
                return None
        return new

    def recurse(assignment: Assignment, doms: Domains) -> Assignment | None:
        if deadline and time.perf_counter() > deadline:
            raise Timeout
        if len(assignment) == len(order):
            return assignment
        var = select_variable(assignment, doms)
        log(f"select {var} ({len(doms[var])} values)")
        for value in doms[var]:
            stats.nodes += 1
            if not consistent(var, value, assignment):
                stats.backtracks += 1
                continue
            assignment[var] = value
            log(f"  try {var} = {value.doctor}/{value.room}/slot{value.slot}")
            new_doms = infer(var, value, assignment, doms) if inference else doms
            if new_doms is not None:
                result = recurse(assignment, new_doms)
                if result is not None:
                    return result
            del assignment[var]
            stats.backtracks += 1
            log(f"  backtrack from {var}")
        return None

    status = "infeasible"
    solution: Assignment | None = None
    try:
        if any(not d for d in domains.values()):
            empty = [k for k, d in domains.items() if not d]
            log(f"empty initial domain for {empty}")
        else:
            solution = recurse({}, domains)
        if solution is not None:
            status = "solved"
    except Timeout:
        status = "timeout"
    stats.runtime_s = time.perf_counter() - t0
    return SolveResult(name, status, dict(solution) if solution else None, stats, trace)
