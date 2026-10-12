"""MRV variable ordering: see `select_variable` in backtracking.py (ordering="mrv")."""

from functools import partial

from clinicflow.solvers.backtracking import backtracking_search

solve_mrv = partial(backtracking_search, ordering="mrv", name="BT+MRV")
