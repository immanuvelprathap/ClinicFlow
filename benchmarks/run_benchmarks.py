"""Run every solver on every instance; write results CSV + a bar chart.

usage: python benchmarks/run_benchmarks.py [--time-limit 30] [--random N]
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from clinicflow.generator import generate
from clinicflow.models import load_instance
from clinicflow.solvers import SOLVERS

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "benchmarks" / "results"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--time-limit", type=float, default=30.0)
    p.add_argument("--random", type=int, default=0, help="also run N seeded random 30-appointment instances")
    args = p.parse_args()
    OUT.mkdir(exist_ok=True)

    instances = [load_instance(f) for f in sorted((ROOT / "data").glob("*.json"))]
    instances += [generate(30, 5, 4, 16, seed=s, tightness=0.6) for s in range(args.random)]

    rows = []
    for inst in instances:
        for name, fn in SOLVERS.items():
            r = fn(inst, time_limit_s=args.time_limit)
            row = {"instance": inst.name, "appointments": len(inst.appointments), **r.row()}
            rows.append(row)
            print(f"{inst.name:<32}{name:<12}{r.status:<11}nodes={r.stats.nodes:<8}"
                  f"backtracks={r.stats.backtracks:<8}ms={r.stats.runtime_s*1000:.1f}")

    with open(OUT / "results.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print("wrote", OUT / "results.csv")

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed; skipping plot")
        return
    names = [n for n in dict.fromkeys(r["instance"] for r in rows)]
    fig, ax = plt.subplots(figsize=(10, 5))
    width = 0.8 / len(SOLVERS)
    for i, s in enumerate(SOLVERS):
        ys = [next(r["nodes"] for r in rows if r["instance"] == n and r["solver"] == s) for n in names]
        ax.bar([x + i * width for x in range(len(names))], [max(y, 1) for y in ys], width, label=s)
    ax.set_xticks([x + 0.4 - width / 2 for x in range(len(names))])
    ax.set_xticklabels(names, rotation=20, ha="right", fontsize=8)
    ax.set_yscale("log")
    ax.set_ylabel("nodes explored (log)")
    ax.set_title("ClinicFlow: search effort per solver")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "nodes.png", dpi=150)
    print("wrote", OUT / "nodes.png")


if __name__ == "__main__":
    main()
