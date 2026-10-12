"""Forward checking inference: see `infer` in backtracking.py (inference="fc")."""

from functools import partial

from clinicflow.solvers.backtracking import backtracking_search

solve_mrv_fc = partial(backtracking_search, ordering="mrv", inference="fc", name="BT+MRV+FC")
