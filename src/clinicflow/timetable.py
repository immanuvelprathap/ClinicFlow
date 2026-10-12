"""Render an assignment as a human-readable timetable (slots x rooms)."""

from __future__ import annotations

from clinicflow.csp import Assignment
from clinicflow.models import Instance


def timetable_grid(instance: Instance, assignment: Assignment) -> list[list[str]]:
    appts = {a.id: a for a in instance.appointments}
    header = ["Slot"] + [r.name for r in instance.rooms]
    rows = [header]
    for slot in instance.slots:
        row = [instance.slot_label(slot)]
        for room in instance.rooms:
            cell = ""
            for appt_id, v in assignment.items():
                if v.slot == slot and v.room == room.id:
                    doc = instance.doctor_by_id[v.doctor]
                    cell = f"{appt_id} {appts[appt_id].patient} ({doc.name})"
            row.append(cell)
        rows.append(row)
    return rows


def format_timetable(instance: Instance, assignment: Assignment) -> str:
    grid = timetable_grid(instance, assignment)
    widths = [max(len(r[i]) for r in grid) for i in range(len(grid[0]))]
    lines = [" | ".join(c.ljust(w) for c, w in zip(r, widths)) for r in grid]
    lines.insert(1, "-+-".join("-" * w for w in widths))
    return "\n".join(lines)
