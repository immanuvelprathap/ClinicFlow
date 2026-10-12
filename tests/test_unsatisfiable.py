import pytest

from clinicflow.solvers import SOLVERS


@pytest.mark.parametrize("name", list(SOLVERS))
def test_all_solvers_report_infeasible(impossible, name):
    res = SOLVERS[name](impossible)
    assert res.status == "infeasible"
    assert res.assignment is None


def test_fc_detects_infeasibility_faster_than_bt(impossible):
    bt, fc = SOLVERS["BT"](impossible), SOLVERS["BT+MRV+FC"](impossible)
    assert fc.stats.nodes <= bt.stats.nodes


def test_empty_domain_is_infeasible_immediately(small):
    small.appointments[0] = small.appointments[0].__class__(
        "A01", "John", "cardiology", (0,), ("ecg",)  # Dr. Ben not available at slot 0
    )
    res = SOLVERS["BT"](small)
    assert res.status == "infeasible" and res.stats.nodes == 0
