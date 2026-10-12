"""Random instance generator (seeded, reproducible) for benchmarks."""

from __future__ import annotations

import random

from clinicflow.models import Appointment, Doctor, Instance, Room

SPECIALTIES = ["general", "cardiology", "dermatology", "orthopedics", "pediatrics"]
EQUIPMENT = {"cardiology": ["ecg"], "dermatology": ["dermatoscope"], "orthopedics": ["xray"]}


def slot_labels(n_slots: int, start_hour: int = 8) -> dict[int, str]:
    return {i: f"{start_hour + i // 2:02d}:{'00' if i % 2 == 0 else '30'}" for i in range(n_slots)}


def generate(
    n_appointments: int,
    n_doctors: int,
    n_rooms: int,
    n_slots: int = 16,
    seed: int = 0,
    tightness: float = 0.5,
    name: str | None = None,
) -> Instance:
    """`tightness` in [0,1]: higher = narrower availability windows = harder instance."""
    rng = random.Random(seed)
    slots = list(range(n_slots))
    specs = SPECIALTIES[: max(2, min(len(SPECIALTIES), n_doctors))]
    doctors = []
    for i in range(n_doctors):
        spec = specs[i % len(specs)]
        n_av = max(4, int(n_slots * (1 - 0.5 * tightness * rng.random())))
        start = rng.randint(0, n_slots - n_av)
        doctors.append(Doctor(f"D{i+1}", f"Dr. {chr(65 + i)}", spec, tuple(range(start, start + n_av))))
    rooms = []
    for i in range(n_rooms):
        eq = []
        for spec, items in EQUIPMENT.items():
            if rng.random() < 0.5:
                eq.extend(items)
        rooms.append(Room(f"R{i+1}", f"Room {i+1}", tuple(sorted(set(eq)))))
    if not any("ecg" in r.equipment for r in rooms):
        rooms[0] = Room(rooms[0].id, rooms[0].name, tuple(sorted(set(rooms[0].equipment) | {"ecg"})))
    appointments = []
    for i in range(n_appointments):
        spec = rng.choice([d.specialty for d in doctors])
        width = max(2, int(n_slots * (1 - tightness * rng.random())))
        start = rng.randint(0, n_slots - width)
        req = tuple(EQUIPMENT.get(spec, [])) if rng.random() < 0.6 else ()
        appointments.append(
            Appointment(f"A{i+1:02d}", f"P{rng.randint(1, max(2, n_appointments * 2 // 3)):03d}", spec,
                        tuple(range(start, start + width)), req)
        )
    return Instance(
        name=name or f"random_{n_appointments}a_{n_doctors}d_{n_rooms}r_s{seed}",
        slots=slots,
        slot_labels=slot_labels(n_slots),
        doctors=doctors,
        rooms=rooms,
        appointments=appointments,
        description=f"Generated with seed={seed}, tightness={tightness}",
    )
