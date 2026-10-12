"""CLI: python -m clinicflow solve data/small_case.json --solver BT+MRV+FC"""

from __future__ import annotations

import argparse
import json

from clinicflow.csp import validate_schedule
from clinicflow.models import load_instance
from clinicflow.solvers import SOLVERS, solve
from clinicflow.timetable import format_timetable


def main() -> None:
    p = argparse.ArgumentParser(prog="clinicflow")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("solve", help="solve one instance")
    s.add_argument("instance")
    s.add_argument("--solver", default="BT+MRV+FC", choices=list(SOLVERS))
    s.add_argument("--trace", action="store_true", help="print search trace")
    s.add_argument("--json", action="store_true", help="machine-readable output")
    c = sub.add_parser("compare", help="run all solvers on one instance")
    c.add_argument("instance")
    c.add_argument("--time-limit", type=float, default=30.0)
    args = p.parse_args()

    inst = load_instance(args.instance)
    if args.cmd == "solve":
        res = solve(inst, args.solver, keep_trace=args.trace)
        if args.json:
            out = res.row()
            out["assignment"] = {k: list(v) for k, v in (res.assignment or {}).items()}
            print(json.dumps(out, indent=2))
            return
        print(f"[{res.solver}] {res.status} in {res.stats.runtime_s*1000:.1f} ms  "
              f"nodes={res.stats.nodes} backtracks={res.stats.backtracks} checks={res.stats.constraint_checks}")
        if args.trace:
            print("\n".join(res.trace))
        if res.assignment:
            errs = validate_schedule(inst, res.assignment)
            print("validator:", "OK" if not errs else errs)
            print(format_timetable(inst, res.assignment))
    else:
        print(f"{'solver':<12}{'status':<11}{'nodes':>8}{'backtr':>8}{'checks':>9}{'pruned':>8}{'ms':>9}")
        for name in SOLVERS:
            r = SOLVERS[name](inst, time_limit_s=args.time_limit)
            st = r.stats
            print(f"{name:<12}{r.status:<11}{st.nodes:>8}{st.backtracks:>8}{st.constraint_checks:>9}"
                  f"{st.pruned_values:>8}{st.runtime_s*1000:>9.1f}")


if __name__ == "__main__":
    main()
