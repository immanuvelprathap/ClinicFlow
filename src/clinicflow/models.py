"""Data model for a ClinicFlow scheduling instance."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import NamedTuple


class Value(NamedTuple):
    """One possible assignment for an appointment: (doctor, room, slot)."""

    doctor: str
    room: str
    slot: int


@dataclass(frozen=True)
class Doctor:
    id: str
    name: str
    specialty: str
    available_slots: tuple[int, ...]


@dataclass(frozen=True)
class Room:
    id: str
    name: str
    equipment: tuple[str, ...] = ()


@dataclass(frozen=True)
class Appointment:
    id: str
    patient: str
    specialty: str
    allowed_slots: tuple[int, ...]
    required_equipment: tuple[str, ...] = ()


@dataclass
class Instance:
    name: str
    slots: list[int]
    slot_labels: dict[int, str]
    doctors: list[Doctor]
    rooms: list[Room]
    appointments: list[Appointment]
    description: str = ""
    doctor_by_id: dict[str, Doctor] = field(init=False, repr=False)
    room_by_id: dict[str, Room] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.doctor_by_id = {d.id: d for d in self.doctors}
        self.room_by_id = {r.id: r for r in self.rooms}

    def slot_label(self, slot: int) -> str:
        return self.slot_labels.get(slot, f"slot {slot}")

    @classmethod
    def from_dict(cls, data: dict) -> "Instance":
        slots = list(data["slots"]) if isinstance(data["slots"], list) else list(range(int(data["slots"])))
        labels = {int(k): v for k, v in data.get("slot_labels", {}).items()}
        doctors = [
            Doctor(d["id"], d.get("name", d["id"]), d["specialty"], tuple(d.get("available_slots", slots)))
            for d in data["doctors"]
        ]
        rooms = [Room(r["id"], r.get("name", r["id"]), tuple(r.get("equipment", ()))) for r in data["rooms"]]
        appointments = [
            Appointment(
                a["id"],
                a["patient"],
                a["specialty"],
                tuple(a.get("allowed_slots", slots)),
                tuple(a.get("required_equipment", ())),
            )
            for a in data["appointments"]
        ]
        return cls(
            name=data.get("name", "instance"),
            slots=slots,
            slot_labels=labels,
            doctors=doctors,
            rooms=rooms,
            appointments=appointments,
            description=data.get("description", ""),
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "slots": self.slots,
            "slot_labels": {str(k): v for k, v in self.slot_labels.items()},
            "doctors": [
                {"id": d.id, "name": d.name, "specialty": d.specialty, "available_slots": list(d.available_slots)}
                for d in self.doctors
            ],
            "rooms": [{"id": r.id, "name": r.name, "equipment": list(r.equipment)} for r in self.rooms],
            "appointments": [
                {
                    "id": a.id,
                    "patient": a.patient,
                    "specialty": a.specialty,
                    "allowed_slots": list(a.allowed_slots),
                    "required_equipment": list(a.required_equipment),
                }
                for a in self.appointments
            ],
        }


def load_instance(path: str | Path) -> Instance:
    with open(path, encoding="utf-8") as fh:
        return Instance.from_dict(json.load(fh))


def save_instance(instance: Instance, path: str | Path) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(instance.to_dict(), fh, indent=2)
