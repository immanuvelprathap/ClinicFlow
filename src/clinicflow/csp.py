"""CSP formulation: variables, domains, constraints and an independent validator.

Variables   : appointments
Domains     : all (doctor, room, slot) triples satisfying the *unary* constraints
              (specialty match, equipment, doctor availability, patient availability)
Constraints : binary "no double booking" constraints between appointment pairs
              (same doctor, same room, or same patient cannot share a slot)
"""

from __future__ import annotations

from clinicflow.models import Appointment, Instance, Value

Domains = dict[str, list[Value]]
Assignment = dict[str, Value]


def build_domains(instance: Instance) -> Domains:
    """Apply unary constraints to enumerate each appointment's legal values."""
    domains: Domains = {}
    for appt in instance.appointments:
        values: list[Value] = []
        for doc in instance.doctors:
            if doc.specialty != appt.specialty:
                continue
            for room in instance.rooms:
                if not set(appt.required_equipment) <= set(room.equipment):
                    continue
                for slot in appt.allowed_slots:
                    if slot in doc.available_slots:
                        values.append(Value(doc.id, room.id, slot))
        domains[appt.id] = values
    return domains


def conflicts(a: Appointment, va: Value, b: Appointment, vb: Value) -> bool:
    """Binary constraint check: True if the two assignments clash."""
    if va.slot != vb.slot:
        return False
    return va.doctor == vb.doctor or va.room == vb.room or a.patient == b.patient


def neighbors(instance: Instance) -> dict[str, list[str]]:
    """Constraint graph: every pair of appointments can clash, so it is complete."""
    ids = [a.id for a in instance.appointments]
    return {i: [j for j in ids if j != i] for i in ids}


def validate_schedule(instance: Instance, assignment: Assignment) -> list[str]:
    """Independent validator. Returns a list of violations (empty == valid).

    Deliberately does not reuse the solver's domain/consistency code so it can
    catch solver bugs.
    """
    errors: list[str] = []
    appts = {a.id: a for a in instance.appointments}
    for appt_id, appt in appts.items():
        if appt_id not in assignment:
            errors.append(f"{appt_id}: unassigned")
            continue
        v = assignment[appt_id]
        doc = instance.doctor_by_id.get(v.doctor)
        room = instance.room_by_id.get(v.room)
        if doc is None or room is None:
            errors.append(f"{appt_id}: unknown doctor/room {v.doctor}/{v.room}")
            continue
        if doc.specialty != appt.specialty:
            errors.append(f"{appt_id}: {doc.id} is {doc.specialty}, needs {appt.specialty}")
        if v.slot not in doc.available_slots:
            errors.append(f"{appt_id}: {doc.id} not available at slot {v.slot}")
        if v.slot not in appt.allowed_slots:
            errors.append(f"{appt_id}: patient not available at slot {v.slot}")
        missing = set(appt.required_equipment) - set(room.equipment)
        if missing:
            errors.append(f"{appt_id}: room {room.id} lacks {sorted(missing)}")
    seen: dict[tuple[str, str, int], str] = {}
    for appt_id, v in assignment.items():
        if appt_id not in appts:
            errors.append(f"{appt_id}: not an appointment of this instance")
            continue
        patient = appts[appt_id].patient
        for label, who in (("doctor", v.doctor), ("room", v.room), ("patient", patient)):
            key = (label, who, v.slot)
            if key in seen:
                errors.append(f"{label} {who} double-booked at slot {v.slot}: {seen[key]} and {appt_id}")
            else:
                seen[key] = appt_id
    return errors
