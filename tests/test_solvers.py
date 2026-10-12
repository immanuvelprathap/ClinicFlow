import pytest

from clinicflow.csp import validate_schedule
from clinicflow.solvers import SOLVERS


@pytest.mark.parametrize("name", list(SOLVERS))
def test_every_solver_finds_valid_schedule(small, name):
    res = SOLVERS[name](small)
    assert res.status == "solved"
    assert validate_schedule(small, res.assignment) == []


@pytest.mark.parametrize("name", list(SOLVERS))
def test_every_solver_solves_medium(medium, name):
    res = SOLVERS[name](medium, time_limit_s=30)
    assert res.status == "solved"
    assert validate_schedule(medium, res.assignment) == []


def test_fc_prunes_and_never_backtracks_on_small(small):
    bt, fc = SOLVERS["BT"](small), SOLVERS["BT+MRV+FC"](small)
    assert fc.stats.pruned_values > 0
    assert fc.stats.backtracks <= bt.stats.backtracks
    assert fc.stats.nodes <= bt.stats.nodes


def test_mrv_picks_most_constrained_first(small):
    res = SOLVERS["BT+MRV"](small, keep_trace=True)
    first = next(line for line in res.trace if line.startswith("select"))
    assert first.startswith("select A01")  # John: cardiology + ECG + 2 slots -> smallest domain


def test_metrics_are_recorded(small):
    res = SOLVERS["BT"](small)
    assert res.stats.nodes > 0 and res.stats.constraint_checks > 0 and res.stats.runtime_s >= 0
    assert set(res.row()) >= {"solver", "status", "nodes", "backtracks", "constraint_checks", "runtime_s"}
