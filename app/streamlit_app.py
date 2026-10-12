"""ClinicFlow demo UI.  Run:  streamlit run app/streamlit_app.py"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from clinicflow.csp import build_domains, validate_schedule
from clinicflow.generator import generate
from clinicflow.models import Instance, load_instance
from clinicflow.solvers import SOLVERS
from clinicflow.timetable import timetable_grid

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

st.set_page_config(page_title="ClinicFlow", page_icon="🏥", layout="wide")
st.title("ClinicFlow — clinic scheduling as a CSP")
st.caption("Backtracking → MRV → Forward Checking → AC-3 (Intro to AI, Lecture 04)")

with st.sidebar:
    st.header("1. Instance")
    source = st.radio("Source", ["Built-in case", "Upload JSON", "Random"])
    if source == "Built-in case":
        files = sorted(DATA.glob("*.json"))
        choice = st.selectbox("Case", files, format_func=lambda p: p.stem)
        instance: Instance = load_instance(choice)
    elif source == "Upload JSON":
        up = st.file_uploader("instance.json", type="json")
        if not up:
            st.stop()
        instance = Instance.from_dict(json.load(up))
    else:
        n_a = st.slider("Appointments", 5, 60, 25)
        n_d = st.slider("Doctors", 2, 8, 5)
        n_r = st.slider("Rooms", 1, 6, 4)
        tight = st.slider("Tightness", 0.0, 1.0, 0.6)
        seed = st.number_input("Seed", 0, 9999, 1)
        instance = generate(n_a, n_d, n_r, 16, seed=int(seed), tightness=tight)
    st.header("2. Solver")
    chosen = st.multiselect("Compare", list(SOLVERS), default=["BT", "BT+MRV", "BT+MRV+FC"])
    time_limit = st.slider("Time limit per solver (s)", 1, 60, 10)
    run = st.button("Solve", type="primary", width="stretch")

st.subheader(instance.name)
if instance.description:
    st.write(instance.description)
c1, c2, c3 = st.columns(3)
c1.metric("Appointments (variables)", len(instance.appointments))
c2.metric("Doctors × Rooms × Slots", f"{len(instance.doctors)} × {len(instance.rooms)} × {len(instance.slots)}")
doms = build_domains(instance)
c3.metric("Σ domain sizes", sum(len(d) for d in doms.values()))

with st.expander("Inspect CSP: variables, domains, constraints"):
    st.markdown(
        "- **Variables**: one per appointment\n"
        "- **Domain**: (doctor, room, slot) triples satisfying specialty, equipment, doctor & patient availability\n"
        "- **Constraints**: no doctor / room / patient double-booked in a slot"
    )
    st.dataframe(pd.DataFrame(
        [{"appointment": a.id, "patient": a.patient, "specialty": a.specialty,
          "equipment": ", ".join(a.required_equipment), "domain size": len(doms[a.id])}
         for a in instance.appointments]), width="stretch", hide_index=True)

if run:
    if not chosen:
        st.warning("Pick at least one solver.")
        st.stop()
    with st.spinner("Solving..."):
        st.session_state["results"] = {
            name: SOLVERS[name](instance, time_limit_s=float(time_limit), keep_trace=True) for name in chosen
        }
        st.session_state["results_for"] = instance.name

results = st.session_state.get("results") if st.session_state.get("results_for") == instance.name else None
if results:
    st.subheader("Solver comparison")
    df = pd.DataFrame([r.row() for r in results.values()])
    df["runtime_ms"] = (df.pop("runtime_s") * 1000).round(2)
    st.dataframe(df, width="stretch", hide_index=True)
    if len(results) > 1:
        st.bar_chart(df.set_index("solver")[["nodes", "backtracks"]])

    best_name = next((n for n, r in results.items() if r.solved), None)
    if best_name is None:
        st.error("No valid schedule exists for this instance (all solvers agree: infeasible).")
        empty = [k for k, d in doms.items() if not d]
        if empty:
            st.write("Appointments with **no legal option at all**:", ", ".join(empty))
        else:
            st.write("Every appointment has options individually, but they cannot all be satisfied together "
                     "(a clash between appointments). See the trace below for the dead end.")
    else:
        res = results[best_name]
        errs = validate_schedule(instance, res.assignment)
        st.subheader(f"Timetable ({best_name})")
        st.success("Independent validator: schedule is conflict-free" if not errs else f"Validator errors: {errs}")
        grid = timetable_grid(instance, res.assignment)
        st.dataframe(pd.DataFrame(grid[1:], columns=grid[0]), width="stretch", hide_index=True)
        st.download_button("Download schedule JSON",
                           json.dumps({k: v._asdict() for k, v in res.assignment.items()}, indent=2),
                           "schedule.json")

    with st.expander("Search trace (how the AI reasoned)"):
        for name, r in results.items():
            st.markdown(f"**{name}** — {len(r.trace)} steps")
            st.code("\n".join(r.trace[:400]) + ("\n..." if len(r.trace) > 400 else ""))
