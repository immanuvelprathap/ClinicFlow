# ClinicFlow — Team Work Plan (per member) + Backup Whole-Solution Plan

> Course: Introduction to AI (Uni Bern) — "AI Startup Studio" team project (20 % of grade).
> Rubric: technical depth 30 · POC functionality 20 · pitch 20 · tech doc 15 · proposal 10 · team process 5.
> Roles below are **proposed**; replace `Member 1..6` with real names from the Team Charter.

## 0. How we work (applies to everyone)

| Rule | Why |
|---|---|
| `main` is always runnable: `pytest` green, `python -m clinicflow compare data/small_case.json` works | Mid-build check-in and final demo can happen any day |
| One branch per member (`feat/<role>`), PR into `main`, one other member reviews | Team-process points + catches bugs |
| Every solver result must pass `validate_schedule()` (written independently of the solvers) | Correctness is 30 % of the grade |
| Weekly 30-min sync: demo your piece, update the table in §4 | Nobody discovers a gap at the end |
| The backup (§3) is already in the repo. Members **replace/improve** pieces, they never start from zero | Zero-risk delivery |

## 1. Roles, deliverables, acceptance criteria

### Member 1 — Product owner & coordination (also presents the pitch)
**Does:** owns the one-sentence problem, the "who hurts / why now" story, the Team Charter, the timeline, and the demo script. Runs the weekly sync and the mid-build check-in.
**Produces:** Team Charter (Phase 1), `docs/pitch_script.md` (6-min, timed), final slide deck (`index.html` already exists — update numbers), check-in demo script.
**Done when:** pitch rehearsed twice under 6 min; every slide answers a rubric line; check-in demo runs from a clean clone in < 5 min.
**Depends on:** results numbers from Member 4, UI from Member 5.

### Member 2 — CSP formalisation (the "math" of the project)
**Does:** writes the formal model: variables, domains, unary vs binary constraints, constraint graph, size of the search space, why it is a CSP and not search/MDP/Bayes. Owns `src/clinicflow/csp.py` and the validator.
**Produces:** `docs/formalisation.md` (2 pages, with the notation used in the proposal + tech doc), `csp.py`, `tests/test_constraints.py`.
**Done when:** every constraint in the doc maps 1-to-1 to a line in `build_domains` / `conflicts` / `validate_schedule`; validator catches 5 hand-made broken schedules (tests).
**Depends on:** nothing — start first. Everyone else builds on this.

### Member 3 — Solver algorithms (Backtracking → MRV → FC → AC-3)
**Does:** implements and explains the solver ladder exactly as in Lecture 04; keeps all variants in one engine so the comparison is fair; adds the search trace used by the UI.
**Produces:** `src/clinicflow/solvers/*`, `tests/test_solvers.py`, `tests/test_unsatisfiable.py`, a 1-page `docs/algorithms.md` (pseudocode from the lecture + what we changed).
**Done when:** all 5 solvers return the same solved/infeasible status on all instances; schedules pass the validator; `BT+MRV+FC` uses ≤ nodes than `BT` on every instance; AC-3 (MAC) is optional but if present has a test.
**Depends on:** Member 2's `csp.py` interface (`build_domains`, `conflicts`).

### Member 4 — Data, scenarios & evaluation
**Does:** builds realistic instances (small hand-made, medium/large generated, one impossible), runs the benchmark, produces the table and plot that go on the results slide and in the tech doc.
**Produces:** `data/*.json`, `src/clinicflow/generator.py`, `benchmarks/run_benchmarks.py`, `benchmarks/results/results.csv` + `nodes.png`, `docs/evaluation.md` (method, seeds, table, 3 bullet findings, limitations).
**Done when:** benchmark reproducible from fixed seeds; table has nodes / backtracks / checks / runtime per solver per instance; at least 5 random seeds reported as mean; impossible case correctly flagged by all solvers.
**Depends on:** Members 2 & 3.

### Member 5 — Demo application & integration
**Does:** Streamlit app (load case → inspect CSP → solve → timetable + metrics + trace → infeasibility explanation); CLI; packaging (`pip install -e .`); README "run in 3 commands".
**Produces:** `app/streamlit_app.py`, `src/clinicflow/__main__.py`, `README.md`, a 60-second screen recording of the demo (backup if Wi-Fi/laptop fails on pitch day).
**Done when:** fresh clone → `pip install -e .[app]` → `streamlit run app/streamlit_app.py` works on Windows and Mac; every rubric "inspectable output" (CSP, schedule, metrics, trace) is visible in the UI.
**Depends on:** Members 2–4 interfaces (already fixed by the backup, so can start day 1).

### Member 6 — Documentation, proposal & QA
**Does:** writes the Technical Proposal (Phase 2, 6 fixed sections) and the final Technical Documentation (3–5 pages); runs QA: tests, reproduces the benchmark, reads every doc against the rubric.
**Produces:** `docs/technical_proposal.md`, `docs/technical_documentation.md`, QA checklist in `docs/qa_checklist.md`, limitations + V2 section.
**Done when:** proposal submitted on time; tech doc contains formalisation, algorithms, evaluation, limitations, how-to-run, honest AI-assistance disclosure; QA checklist all ticked the day before the pitch.
**Depends on:** everyone — but the skeleton exists in `PROJECT_PACKAGE.md`.

*5-person team:* merge Member 6 into Members 1 (proposal/doc) and 4 (QA).

## 2. Timeline (dependency order, not calendar — fit to ILIAS due dates)

| Week | Milestone | Owner(s) | Gate |
|---|---|---|---|
| W1 | Team Charter + problem pitch (1 page) submitted | M1, M6 | Submitted on ILIAS |
| W1 | Formalisation v1 + `csp.py` + validator | M2 | `tests/test_constraints.py` green |
| W2 | Basic Backtracking + MRV + small & impossible cases | M3, M4 | All tests green, both cases correct |
| W2–3 | Technical Proposal (2–3 pages) | M6 with M2/M3 | Submitted; uses formalisation notation |
| W3 | Forward Checking + medium/large generator | M3, M4 | FC ≤ BT nodes on every instance |
| W4 | Streamlit demo v1 + CLI + README | M5 | Fresh clone runs in 3 commands |
| W4 | **Mid-build check-in** (live demo + metrics) | M1 presents, all | Instructor feedback logged in `docs/checkin_notes.md` |
| W5 | Benchmark table + plot; AC-3/MAC (stretch) | M4, M3 | `results.csv`, `nodes.png`, 5 seeds |
| W6 | Tech doc draft; deck numbers updated; demo recording | M6, M1, M5 | Internal review against rubric |
| W7 | QA, rehearsals ×2, final submission | all | Checklist ticked, deck < 6 min |

## 3. Backup: the whole solution (already built, in this repo)

Everything below exists on `main` today so the team can never be blocked:

| Piece | File | Status |
|---|---|---|
| Data model + JSON loader | `src/clinicflow/models.py` | done |
| Domains, constraints, independent validator | `src/clinicflow/csp.py` | done |
| BT / BT+MRV / BT+FC / BT+MRV+FC / BT+MRV+MAC (AC-3) | `src/clinicflow/solvers/` | done |
| Metrics (nodes, backtracks, checks, pruned, runtime) + trace | `src/clinicflow/metrics.py` | done |
| Instances: small (BernCare), medium, large, impossible | `data/*.json`, `benchmarks/make_data.py` | done |
| Random generator (seeded) | `src/clinicflow/generator.py` | done |
| Benchmark runner → CSV + log-scale plot | `benchmarks/run_benchmarks.py` | done |
| CLI (`solve`, `compare`, `--trace`) | `src/clinicflow/__main__.py` | done |
| Streamlit demo | `app/streamlit_app.py` | done |
| Tests (26) | `tests/` | green |
| Pitch deck (with in-browser demo) + project package | `index.html`, `PROJECT_PACKAGE.md` | done |
| Formalisation / algorithms / evaluation / proposal / tech-doc text | `docs/` | **to write** (M2, M3, M4, M6) — skeletons in `PROJECT_PACKAGE.md` |

Reference numbers from the backup (`python benchmarks/run_benchmarks.py`), large case = 40 appointments, 6 doctors, 5 rooms, 16 slots:

| Solver | Nodes | Backtracks | Runtime |
|---|---|---|---|
| BT | 209 873 | 209 833 | ~590 ms |
| BT+MRV | 851 | 811 | ~2 ms |
| BT+FC | 44 | 4 | ~7 ms |
| BT+MRV+FC | 40 | 0 | ~10 ms |
| BT+MRV+MAC | 40 | 0 | ~21 ms |

Impossible case: all solvers report `infeasible`; FC detects it at node 1, plain BT needs 2.

**Integration rule:** a member's version replaces the backup piece only when its tests pass *and* the benchmark still runs. If a member's piece is late, the backup piece ships and the member documents/explains it instead (still a contribution for the tech doc and Q&A).

## 4. Progress table (update weekly)

| Member | Piece | Branch | Status | Blocker |
|---|---|---|---|---|
| M1 | | | | |
| M2 | | | | |
| M3 | | | | |
| M4 | | | | |
| M5 | | | | |
| M6 | | | | |

## 5. Q&A prep — each member must be able to answer
- M2: "Why is this a CSP and not A* or an MDP?" — deterministic, fully observable, no sequential reward; we need *any* consistent assignment, not a path.
- M3: "What does forward checking add over backtracking?" — prunes neighbours' domains after each assignment; detects dead-ends immediately (0 backtracks vs 209 833 on the large case).
- M3: "What is AC-3 / MAC and why is it slower here?" — propagates through the whole constraint graph; more checks per node (112 k vs 57 k) with no extra pruning on our instances — honest finding.
- M4: "How do you know the schedule is correct?" — independent validator written separately from the solvers; 26 tests; impossible case.
- M1/M6: "Limitations?" — single-slot appointments, hard constraints only, no preferences/optimisation (V2: soft constraints via weighted CSP / local search min-conflicts).
