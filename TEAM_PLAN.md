# ClinicFlow — Team Work Plan (per member) + Backup Whole-Solution Plan

> Course: Introduction to AI (Uni Bern) — "AI Startup Studio" team project (20 % of grade).
> Rubric: technical depth 30 · POC functionality 20 · pitch 20 · tech doc 15 · proposal 10 · team process 5.
> Team (from the Team Charter): Emma Jakobsson, Immanuvel Sagayaraju, Katharina Kalbermatter, Louis Gérard, Pranamya Kunjal.
> Charter areas → plan: Technical development = Immanuvel · Research = Katharina (also logistics/contact) · Evaluation = Louis · Documentation = Emma · Presentation = Pranamya.
> Everyone owns one area but supports the others (as agreed in the charter).

## 0. How we work (applies to everyone)

| Rule | Why |
|---|---|
| `main` is always runnable: `pytest` green, `python -m clinicflow compare data/small_case.json` works | Mid-build check-in and final demo can happen any day |
| One branch per member (`feat/<role>`), PR into `main`, one other member reviews | Team-process points + catches bugs |
| Every solver result must pass `validate_schedule()` (written independently of the solvers) | Correctness is 30 % of the grade |
| Weekly 30-min sync: demo your piece, update the table in §4 | Nobody discovers a gap at the end |
| The backup (§3) is already in the repo. Members **replace/improve** pieces, they never start from zero | Zero-risk delivery |

## 1. Roles, deliverables, acceptance criteria

### Pranamya — Presentation (pitch owner)
**Does:** owns the startup story (problem, who hurts, why now, how it reaches users), the 6-minute pitch, the demo script for the mid-build check-in and final day.
**Produces:** `docs/pitch_script.md` (timed), final deck (`index.html` exists — update results numbers and team slide), check-in demo script, Q&A answer sheet.
**Done when:** pitch rehearsed twice under 6 min; every slide answers a rubric line; demo runs from a clean clone in < 5 min.
**Depends on:** Louis's results numbers, Immanuvel's UI.

### Katharina — Research + logistics (CSP formalisation, course link)
**Does:** team contact/logistics (meetings, ILIAS deadlines, submissions). Research: the formal CSP model — variables, domains, unary vs binary constraints, constraint graph, search-space size — and the justification from Lecture 04 (why CSP, not A*/MDP/Bayes; what BT/MRV/FC/AC-3 are).
**Produces:** `docs/formalisation.md` (2 pages, notation reused by proposal + tech doc), `docs/algorithms.md` (lecture pseudocode vs our implementation), deadline table in §2 kept current.
**Done when:** every constraint in the doc maps 1-to-1 to a line in `csp.py` (`build_domains`, `conflicts`, `validate_schedule`); each solver in `solvers/` is explained with its lecture slide reference.
**Depends on:** nothing — start first; reviews Immanuvel's code against the formalisation.

### Immanuvel — Technical development (solvers, app, integration)
**Does:** owns the code: `csp.py`, the solver ladder in one engine (`backtracking_search` with `ordering` and `inference` switches), the search trace, the Streamlit demo, CLI, packaging, PR reviews/merges into `main`.
**Produces:** `src/clinicflow/*`, `app/streamlit_app.py`, `tests/`, README "run in 3 commands", 60-second demo recording as pitch-day backup.
**Done when:** all 5 solvers agree on solved/infeasible on every instance; every schedule passes the independent validator; `BT+MRV+FC` ≤ `BT` nodes on every instance; fresh clone → `pip install -e .[app,dev]` → `streamlit run app/streamlit_app.py` works on Windows and Mac.
**Depends on:** Katharina's formalisation (interfaces already fixed by the backup, so can start day 1).

### Louis — Evaluation (data, benchmarks, results)
**Does:** builds the scenarios (hand-made small, generated medium/large with fixed seeds, impossible), runs the benchmark, produces the table/plot for the results slide and tech doc, writes the honest findings (e.g. AC-3/MAC prunes nothing extra here but costs 2× checks).
**Produces:** `data/*.json`, `generator.py` tuning, `benchmarks/results/results.csv` + `nodes.png`, `docs/evaluation.md` (method, seeds, table, 3 findings, limitations).
**Done when:** benchmark reproducible from seeds; nodes / backtracks / checks / runtime per solver per instance; ≥ 5 random seeds reported as mean; impossible case flagged by all solvers.
**Depends on:** Immanuvel's solvers (available now).

### Emma — Documentation + QA (proposal, tech doc)
**Does:** writes the Technical Proposal (Phase 2, 6 fixed sections) and the final Technical Documentation (3–5 pages); runs QA: tests, reproduces the benchmark, reads every doc and slide against the rubric.
**Produces:** `docs/technical_proposal.md`, `docs/technical_documentation.md`, `docs/qa_checklist.md`, limitations + V2 section, AI-assistance disclosure.
**Done when:** proposal submitted on time; tech doc contains formalisation, algorithms, evaluation, limitations, how-to-run; QA checklist all ticked the day before the pitch.
**Depends on:** everyone — skeletons exist in `PROJECT_PACKAGE.md`.

## 2. Timeline (dependency order, not calendar — fit to ILIAS due dates)

| Week | Milestone | Owner(s) | Gate |
|---|---|---|---|
| W1 | Team Charter + problem pitch (1 page) submitted | Pranamya, Emma | Submitted on ILIAS |
| W1 | Formalisation v1 + `csp.py` + validator | Katharina | `tests/test_constraints.py` green |
| W2 | Basic Backtracking + MRV + small & impossible cases | Immanuvel, Louis | All tests green, both cases correct |
| W2–3 | Technical Proposal (2–3 pages) | Emma with Katharina/Immanuvel | Submitted; uses formalisation notation |
| W3 | Forward Checking + medium/large generator | Immanuvel, Louis | FC ≤ BT nodes on every instance |
| W4 | Streamlit demo v1 + CLI + README | Immanuvel | Fresh clone runs in 3 commands |
| W4 | **Mid-build check-in** (live demo + metrics) | Pranamya presents, all | Instructor feedback logged in `docs/checkin_notes.md` |
| W5 | Benchmark table + plot; AC-3/MAC (stretch) | Louis, Immanuvel | `results.csv`, `nodes.png`, 5 seeds |
| W6 | Tech doc draft; deck numbers updated; demo recording | Emma, Pranamya, Immanuvel | Internal review against rubric |
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
| Formalisation / algorithms / evaluation / proposal / tech-doc text | `docs/` | **to write** (Katharina, Louis, Emma) — skeletons in `PROJECT_PACKAGE.md` |

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
| Emma | proposal, tech doc, QA | | | |
| Immanuvel | solvers, app, integration | | | |
| Katharina | formalisation, algorithms doc, logistics | | | |
| Louis | data, benchmarks, evaluation doc | | | |
| Pranamya | pitch, demo script, deck | | | |

## 5. Q&A prep — each member must be able to answer
- Katharina: "Why is this a CSP and not A* or an MDP?" — deterministic, fully observable, no sequential reward; we need *any* consistent assignment, not a path.
- Immanuvel: "What does forward checking add over backtracking?" — prunes neighbours' domains after each assignment; detects dead-ends immediately (0 backtracks vs 209 833 on the large case).
- Immanuvel: "What is AC-3 / MAC and why is it slower here?" — propagates through the whole constraint graph; more checks per node (112 k vs 57 k) with no extra pruning on our instances — honest finding.
- Louis: "How do you know the schedule is correct?" — independent validator written separately from the solvers; 26 tests; impossible case.
- Pranamya/Emma: "Limitations?" — single-slot appointments, hard constraints only, no preferences/optimisation (V2: soft constraints via weighted CSP / local search min-conflicts).
