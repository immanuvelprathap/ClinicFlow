# ClinicFlow — clinic appointment scheduling as a CSP

Intro to AI (University of Bern) team project. Appointments are modelled as a **Constraint Satisfaction Problem**
and solved with the Lecture-04 ladder **Backtracking → MRV → Forward Checking → AC-3 (MAC)**, with metrics
(nodes, backtracks, constraint checks, runtime) to compare them.

- Pitch deck (iPad-friendly, with live in-browser demo): https://immanuvelprathap.github.io/ClinicFlow/ (or https://raw.githack.com/immanuvelprathap/ClinicFlow/main/index.html)
- Project package (charter, proposal skeleton, templates): [`PROJECT_PACKAGE.md`](PROJECT_PACKAGE.md)
- Team work plan + backup plan: [`TEAM_PLAN.md`](TEAM_PLAN.md)

## Run in 3 commands

```bash
pip install -e .[app,dev]
python -m clinicflow compare data/large_case.json      # all solvers, one table
streamlit run app/streamlit_app.py                     # demo UI
```

Other useful commands:

```bash
python -m clinicflow solve data/small_case.json --solver BT+MRV+FC --trace   # timetable + reasoning trace
python -m pytest                                                             # 26 tests
python benchmarks/run_benchmarks.py --random 5                               # results.csv + nodes.png
```

## Results (large case: 40 appointments, 6 doctors, 5 rooms, 16 slots)

| Solver | Nodes | Backtracks | Runtime |
|---|---|---|---|
| BT | 209 873 | 209 833 | ~590 ms |
| BT+MRV | 851 | 811 | ~2 ms |
| BT+MRV+FC | 40 | 0 | ~10 ms |
| BT+MRV+MAC | 40 | 0 | ~21 ms |

All solvers agree on the impossible case (`infeasible`); every schedule is checked by an independent validator.

## Layout

```
src/clinicflow/   models.py csp.py metrics.py generator.py timetable.py solvers/{backtracking,ac3,mrv,forward_checking}.py
data/             small_case.json medium_case.json large_case.json impossible_case.json
tests/            test_constraints.py test_solvers.py test_unsatisfiable.py
benchmarks/       run_benchmarks.py make_data.py results/
app/              streamlit_app.py
```

Instance JSON format: see `data/small_case.json` (doctors with specialty + available slots, rooms with equipment,
appointments with specialty, allowed slots and required equipment).
