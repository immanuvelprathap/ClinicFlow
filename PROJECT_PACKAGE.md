# ClinicFlow — Complete Project Package
### Introduction to AI (Uni Bern, HS 2026) — Semester Project "AI Startup Studio"

One-sentence version: **ClinicFlow is a small AI clinic scheduler. Appointments are modelled as a Constraint Satisfaction Problem (CSP); we compare plain Backtracking with MRV and Forward Checking to automatically produce a conflict-free schedule.**

Everything below is a fill-in template. Items in `[brackets]` are for the team to complete. Dates are inferred from "Week 3 of project" with course start 15 Sep 2026 — confirm on ILIAS.

---

## 0. Quick reference

| Item | Value |
|---|---|
| Project weight | 20% of course grade |
| Rubric | Technical depth 30% · POC 20% · Pitch 20% · Tech doc 15% · Proposal 10% · Team process 5% |
| Phase 1 | Team Charter + Problem Pitch, 1 page — week 3 (≈ week of 29 Sep, confirm) |
| Phase 2 | Technical Proposal, 2–3 pages, 6 fixed sections — after probabilistic-methods unit (≈ after Lec 08/09) |
| Phase 3 | Build sprint + mid-build check-in demo |
| Phase 4 | 6-min pitch + Q&A, POC demo (bring backup recording), 3–5 page tech doc — finals week / last session |
| Minimum POC bar | Technique runs on realistic input; output is inspectable (here: the CSP solution + solver statistics) |
| Traps to avoid | "doesn't need AI" · overscoping · pitch recycled as doc · no "why now" · data too late |

Abbreviations: **CSP** Constraint Satisfaction Problem · **BT** Backtracking · **MRV** Minimum Remaining Values · **FC** Forward Checking · **AC-3** Arc Consistency · **POC** Proof of Concept.

---

## 1. Deliverable 1 — Team Charter + Problem Pitch (1 page)

### 1a. Problem pitch (top half)

**ClinicFlow — Constraint-Based Clinic Scheduling**

**Problem.** Outpatient clinics must place many appointments across doctors, rooms, equipment and time slots while respecting availability, specialty and equipment rules. A coordinator can do this by hand for 3 appointments; at 30+ appointments the interacting constraints make manual scheduling slow and error-prone (double bookings, wrong room, unavailable doctor).

**Who hurts.** Clinic coordinators / front-desk staff in small and mid-size clinics (typically 3–8 clinicians); indirectly patients (waiting, rescheduling) and clinicians (idle or overloaded slots).

**AI approach.** We formulate scheduling as a **Constraint Satisfaction Problem**: each appointment is a variable, its domain is the set of feasible (doctor, room, time-slot) triples, and the constraints are the clinic rules. We solve it with backtracking search improved by MRV ordering and forward checking, as taught in Lecture 04.

**Why AI rather than if-statements.** An if-statement can check whether *one* assignment violates a rule. The task is to find a *complete* assignment for all appointments simultaneously where a locally valid early choice can make the whole schedule impossible later — a combinatorial search problem, which is exactly what CSP methods address.

**Why now.** Small clinics are digitising booking but still schedule with spreadsheets; lightweight open-source constraint solving on a laptop is now trivially cheap, so this no longer needs enterprise hospital software.

**Proof of concept.** Input: JSON describing doctors, rooms, time slots, appointments and rules. Output: a valid timetable (or a proof that the instance is infeasible) plus solver statistics (nodes explored, backtracks, runtime) for BT vs BT+MRV vs BT+MRV+FC.

### 1b. Team charter (bottom half)

| Member | Charter area | Primary responsibility in ClinicFlow |
|---|---|---|
| **Katharina Kalbermatter** — logistics point of contact | Research | CSP formalisation (variables, domains, constraints), algorithm explanation from Lecture 04, deadlines/ILIAS submissions |
| **Immanuvel Sagayaraju** | Technical development | Solvers (BT, MRV, FC, AC-3), tests, Streamlit demo, integration of everyone's work into `main` |
| **Louis Gérard** | Evaluation | Scenario/data generation, benchmark harness, results tables and figures |
| **Emma Jakobsson** | Documentation | Technical proposal, final technical documentation, QA against the rubric |
| **Pranamya Kunjal** | Presentation | 6-minute pitch, demo script, Q&A preparation |

Everyone owns one area but supports the others (see `TEAM_PLAN.md` for deliverables, acceptance criteria and weekly schedule).

**Meeting cadence.** Approximately weekly (online or in person), with extra coordination before deadlines. Quick communication on WhatsApp; all project material on GitHub (`immanuvelprathap/ClinicFlow`). Each PR has one author and one reviewer.

---

## 2. Formal CSP model (used in proposal §3 and tech doc §3)

### Sets

- Appointments \(A = \{a_1,\dots,a_n\}\)
- Doctors \(P\), each with specialty \(spec(p)\) and availability \(avail(p) \subseteq T\)
- Rooms \(R\), each with equipment set \(equip(r)\)
- Time slots \(T = \{t_1,\dots,t_k\}\) (e.g. 30-min slots of one working day)

### Variables
\(X_i\) = the assignment of appointment \(a_i\), for \(i = 1..n\).

### Domains
\(D_i \subseteq P \times R \times T\), pre-filtered by unary constraints:

\[
D_i = \{(p,r,t) \;:\; spec(p) = need(a_i),\; req(a_i) \subseteq equip(r),\; t \in avail(p) \cap window(a_i)\}
\]

### Constraints

| ID | Type | Constraint | Meaning |
|---|---|---|---|
| C1 | unary | \(spec(p) = need(a_i)\) | doctor has the required specialty |
| C2 | unary | \(req(a_i) \subseteq equip(r)\) | room has required equipment (e.g. ECG) |
| C3 | unary | \(t \in avail(p)\) | doctor is available at that time |
| C4 | unary | \(t \in window(a_i)\) | patient availability window |
| C5 | binary | \(t_i = t_j \Rightarrow p_i \neq p_j\) | a doctor sees one patient at a time |
| C6 | binary | \(t_i = t_j \Rightarrow r_i \neq r_j\) | a room hosts one appointment at a time |
| C7 (optional) | binary | \(patient(a_i)=patient(a_j) \Rightarrow t_i \neq t_j\) | same patient not double-booked |
| C8 (optional, V2) | soft | minimise gaps / prefer same doctor for follow-ups | optimisation, not required for POC |

For multi-slot appointments (duration \(d_i\) slots), replace \(t_i = t_j\) by *overlap*\((t_i,d_i,t_j,d_j)\).

### Solution
A complete assignment \((X_1,\dots,X_n)\) with \(X_i \in D_i\) satisfying C1–C7, or a certificate "no satisfying assignment exists".

### Worked mini-example (BernCare Clinic)

Doctors: Anna (General, all day), Ben (Cardiology, all day), Clara (General, all day). Rooms: R1 (plain), R2 (ECG). Slots: 09, 10, 11, 13.

| Appointment | Needs | Window |
|---|---|---|
| Sarah | General | 09–11 |
| John | Cardio + ECG | 09–12 |
| Maria | General | 10–12 |
| David | Cardio + ECG | 11–14 |
| Lisa | General | 13–15 |

Pre-filtered domains: \(D_{John} = \{(Ben,R2,09),(Ben,R2,10),(Ben,R2,11)\}\), \(D_{David} = \{(Ben,R2,11),(Ben,R2,13)\}\), \(D_{Lisa} = \{(Anna|Clara, R1|R2, 13)\}\), etc. MRV picks David first (2 values). One solution:

| Time | Doctor | Patient | Room |
|---|---|---|---|
| 09:00 | Anna | Sarah | R1 |
| 09:00 | Ben | John | R2 |
| 10:00 | Clara | Maria | R1 |
| 11:00 | Ben | David | R2 |
| 13:00 | Anna | Lisa | R1 |

---

## 3. Algorithms to implement and compare

1. **BT** — chronological backtracking (Lecture 04 algorithm), variables in input order, values in domain order.
2. **BT + MRV** — choose the unassigned variable with the fewest legal values; tie-break by degree heuristic (most constraints on remaining variables).
3. **BT + MRV + FC** — after each assignment, remove inconsistent values from neighbours' domains; backtrack immediately if any domain empties.
4. **BT + MRV + AC-3** (stretch) — arc consistency after each assignment (MAC).
5. **Min-conflicts local search** (stretch / fallback for large instances) — not complete; report separately.

Metrics recorded for every run: `nodes_expanded`, `backtracks`, `constraint_checks`, `runtime_ms`, `status ∈ {solved, infeasible, timeout}`.

Correctness checks: an independent `validate(schedule)` function re-checks every constraint on the output; all solvers must agree on `status` for every instance; on tiny instances, results are compared to brute-force enumeration.

---

## 4. Deliverable 2 — Technical Proposal skeleton (2–3 pages, 10%)

1. **Problem statement** (¼ p) — "Given a set of appointments, clinicians, rooms, time slots and compatibility constraints, determine a complete assignment in which all hard constraints are satisfied, or report infeasibility." Include one sentence on the user (coordinator) and scale (≤ 40 appointments/day).
2. **Chosen technique + justification** (½ p) — CSP. Compare with alternatives from the course: *Search (A\*)* — no meaningful path cost, all variables assigned simultaneously; *Bayesian networks* — problem is deterministic, nothing to infer; *MDP* — no sequential stochastic dynamics or rewards. CSP exactly matches: discrete variables, finite domains, hard constraints; scheduling/timetabling is the textbook CSP application (Lec 04).
3. **Formalization** (½–¾ p) — Section 2 above, with the 5-appointment example.
4. **Data / environment** (¼ p) — Synthetic instances generated by our own script (`generate_instance(n_appts, n_docs, n_rooms, n_slots, seed, tightness)`); three fixed benchmark files (`small`, `medium`, `impossible`); no patient data, no external systems. Python 3.11, Streamlit, pytest; runs on a laptop.
5. **Definition of done** (¼ p) — "For an instance with ≥ 20 appointments, 4 clinicians, 4 rooms and ≥ 8 slots, the system returns a valid schedule (verified by an independent checker) or correctly reports infeasibility in < 5 s, and the UI shows the timetable plus per-algorithm statistics for BT, BT+MRV, BT+MRV+FC."
6. **Risks + fallback** (¼ p) — Risk 1: exponential blow-up on tight instances → cap with node/time limit, report timeout, add FC/AC-3. Risk 2: AC-3 / multi-slot durations too complex → fallback is BT+MRV+FC with single-slot appointments, evaluated thoroughly. Risk 3: team member unavailability → every module has a named backup.

---

## 5. Repository layout

```
clinicflow/
├── README.md
├── requirements.txt          # streamlit, pytest, pandas, matplotlib
├── data/
│   ├── small_case.json       # 5 appts (BernCare example)
│   ├── medium_case.json      # 20 appts
│   ├── large_case.json       # 30-40 appts
│   └── impossible_case.json  # provably infeasible
├── src/clinicflow/
│   ├── models.py             # Doctor, Room, Appointment, Instance (dataclasses) + JSON loader
│   ├── csp.py                # build_domains(), constraint functions, validate()
│   ├── solvers/
│   │   ├── backtracking.py
│   │   ├── mrv.py
│   │   ├── forward_checking.py
│   │   └── ac3.py            # stretch
│   ├── metrics.py            # SolverStats dataclass
│   └── generator.py          # synthetic instance generator
├── app/streamlit_app.py      # tabs: Input · Solution · Algorithm Analysis
├── benchmarks/run_benchmarks.py → results/benchmark_results.csv + plots
└── tests/
    ├── test_constraints.py
    ├── test_solvers.py       # all solvers agree; outputs validate
    └── test_unsatisfiable.py
```

Instance JSON shape:

```json
{
  "slots": ["09:00","10:00","11:00","13:00"],
  "doctors": [{"id":"anna","specialty":"general","available":["09:00","10:00","11:00","13:00"]}],
  "rooms":   [{"id":"R2","equipment":["ecg"]}],
  "appointments": [{"id":"john","patient":"John","specialty":"cardiology",
                    "equipment":["ecg"],"window":["09:00","10:00","11:00"],"duration":1}]
}
```

---

## 6. Engineering backlog (status: implemented)

Rules for every item: the CSP formulation is owned by the team and not changed without agreement; only techniques from the course (no LLMs, external optimisers or ML libraries); every item ships with tests, reproducible inputs and documented outputs; one team member reviews before merge.

All items below are implemented in the repository (see §12 for file locations); owners now refine and document them.

| # | Ticket | Acceptance criterion | Owner / reviewer |
|---|---|---|---|
| D01 | Repo scaffold + CI (pytest) | `pytest` runs green on empty suite; README explains setup | Immanuvel |
| D02 | `models.py` + JSON loader + `small_case.json` | Loads BernCare example; dataclasses typed; loader rejects malformed input | Katharina |
| D03 | `csp.py`: domain construction + constraints + `validate()` | Unit tests for C1–C7; `validate` accepts the hand-made solution and rejects 3 broken variants | Katharina |
| D04 | Naive backtracking solver + `SolverStats` | Solves small case; stats recorded; brute-force agreement on ≤ 6-appointment instances | Immanuvel |
| D05 | MRV (+ degree tie-break) | Same `status` as D04 on all data files; fewer or equal nodes on medium case | Immanuvel |
| D06 | Forward checking | Same `status`; domain-wipeout detected; fewer nodes than D05 on medium case | Immanuvel |
| D07 | Instance generator + `impossible_case.json` | Deterministic by seed; `tightness` parameter; impossible case proven infeasible by all solvers | Louis |
| D08 | Benchmark runner + CSV + plots | Runs 3 solvers × 4 instances × 5 seeds; produces `benchmark_results.csv` and 2 PNG charts | Louis |
| D09 | Streamlit app (3 tabs) | Load/edit instance → run → timetable grid → stats table; infeasible message shown for impossible case | Immanuvel |
| D10 | AC-3 / MAC (stretch) | Same `status`; nodes ≤ FC on large case | Immanuvel |
| D11 | Demo script + backup recording checklist | 2-minute scripted run reproducible from a fresh clone | Pranamya / Emma |

---

## 7. Evaluation plan (feeds tech doc §4 and pitch slide)

**Instances.** small (5), medium (20), large (30–40), impossible; each at tightness levels loose/medium/tight; 5 random seeds each.

**Table 1 — search effort**

| Instance | Solver | Nodes | Backtracks | Constraint checks | Runtime (ms) | Status |
|---|---|---|---|---|---|---|
| medium-tight | BT | … | … | … | … | solved |
| medium-tight | BT+MRV | … | … | … | … | solved |
| medium-tight | BT+MRV+FC | … | … | … | … | solved |
| impossible | all | … | … | … | … | infeasible |

**Figure 1.** Nodes expanded vs. number of appointments (log-y), one line per solver.
**Figure 2.** Runtime vs. tightness for n = 30.

**Claims to support.** (i) all solvers are correct (validator + agreement); (ii) MRV and FC reduce search effort by orders of magnitude on tight instances; (iii) the system correctly detects infeasibility; (iv) limits: where BT times out.

---

## 8. Mid-build check-in script (Phase 3)

1. Load `medium_case.json` (20 appointments). 2. Run BT → show nodes/backtracks. 3. Run BT+MRV+FC → show the drop. 4. Show generated timetable and the validator's OK. 5. Load `impossible_case.json` → "No satisfying assignment exists" with the reason (e.g. two ECG appointments forced into one slot). 6. Show the open backlog and who owns what.

---

## 9. Final pitch — 6 minutes

| Time | Slide | Content |
|---|---|---|
| 0:00–0:40 | Problem | Coordinator with 30 appointments, 5 doctors, 4 rooms; double-booking story |
| 0:40–1:20 | Who hurts / how big | Number of small clinics in CH; time lost per week; rescheduling cost |
| 1:20–1:55 | Solution | ClinicFlow in one sentence + screenshot |
| 1:55–3:35 | Live demo (backup video ready) | Input → Generate → timetable → Algorithm Analysis → impossible case |
| 3:35–4:35 | Why AI | CSP: variables/domains/constraints; BT → MRV → FC in one diagram |
| 4:35–5:10 | Results | Figure 1 + one table row: 18 k nodes → 1.2 k nodes |
| 5:10–5:35 | Users / why now / adoption | Coordinators; spreadsheet replacement; plug-in to existing booking tools |
| 5:35–6:00 | Limitations + V2 | Soft constraints/optimisation, multi-day, preferences, real data pilot |

Q&A prep — every member must be able to answer: why this problem, why CSP, how it is formalised, how BT/MRV/FC work, how we know it is correct, what its limits are.

---

## 10. Technical documentation template (3–5 pages, 15%)

1. **Problem & system overview** (½ p)
2. **Architecture** (½ p) — diagram: Instance JSON → Parser → Variables/Domains/Constraints → Solver {BT | MRV | FC | AC-3} → Solution + Stats → Validator → Streamlit UI
3. **Algorithm & formalisation** (1 p) — Section 2 + pseudocode of BT-MRV-FC; list any deviation from the proposal
4. **Experimental evaluation** (1 p) — Table 1, Figures 1–2, correctness checks, what did not work
5. **Limitations & V2** (½ p) — hard constraints only, single day, synthetic data; V2: soft constraints (weighted CSP / local search), multi-day, real pilot
6. **Individual contributions** (½ p) — one paragraph per member, aligned with the charter

---

## 11. Semester timeline

| Period | Objective | Frozen output |
|---|---|---|
| 22–29 Sep | Choose project, formalise, tiny feasibility solver | Charter + 1-page pitch submitted |
| Oct | D01–D06 | Solver v0.1 (BT, MRV, FC) on small/medium |
| After Lec 08/09 (≈ early Nov, mind midterm 3 Nov) | Proposal | 2–3 page proposal submitted |
| Nov | D07–D09 | Demo v0.2, mid-build check-in |
| Late Nov | D08 results, D10 stretch | Benchmark tables/figures |
| ≈ 5 Dec | Code freeze | v1.0 |
| 5–15 Dec | Docs, pitch rehearsal, backup recording | Final package |

---

## 12. What is implemented (repository `immanuvelprathap/ClinicFlow`)

| Component | Where | Status |
|---|---|---|
| Data model + JSON loader | `src/clinicflow/models.py` | done |
| Domains, binary constraints, independent validator | `src/clinicflow/csp.py` | done |
| Solvers BT · BT+MRV · BT+FC · BT+MRV+FC · BT+MRV+MAC (AC-3) | `src/clinicflow/solvers/` | done |
| Metrics (nodes, backtracks, checks, pruned values, runtime) + search trace | `src/clinicflow/metrics.py` | done |
| Instances small (BernCare) / medium / large / impossible + seeded generator | `data/`, `src/clinicflow/generator.py` | done |
| Benchmark runner → `results.csv` + log-scale chart | `benchmarks/run_benchmarks.py` | done |
| CLI (`solve`, `compare`, `--trace`) | `python -m clinicflow` | done |
| Streamlit demo (load → inspect CSP → solve → timetable, metrics, trace, infeasibility) | `app/streamlit_app.py` | done |
| Tests (26) | `tests/` | green |
| Pitch deck with in-browser demo | `index.html` | done — update after final benchmark |
| Formalisation, algorithms, evaluation texts; proposal; tech doc; pitch script | `docs/` | **to write** (Katharina, Louis, Emma, Pranamya) |

Measured results, large case (40 appointments, 6 doctors, 5 rooms, 16 slots):

| Solver | Nodes | Backtracks | Runtime |
|---|---|---|---|
| BT | 209 873 | 209 833 | ~590 ms |
| BT+MRV | 851 | 811 | ~2 ms |
| BT+FC | 44 | 4 | ~7 ms |
| BT+MRV+FC | 40 | 0 | ~10 ms |
| BT+MRV+MAC | 40 | 0 | ~21 ms |

Impossible case: all solvers report `infeasible`; FC detects it at node 1.

**Links**

- Pitch deck: https://immanuvelprathap.github.io/ClinicFlow/
- Live Streamlit demo: https://immanuvelprathap-clinicflow.streamlit.app *(deploy once on share.streamlit.io: New app → repo `immanuvelprathap/ClinicFlow` → branch `main` → file `app/streamlit_app.py`)*
- Run locally: `pip install -e .[app,dev]` · `python -m clinicflow compare data/large_case.json` · `streamlit run app/streamlit_app.py`
