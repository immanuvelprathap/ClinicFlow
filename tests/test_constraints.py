from clinicflow.csp import build_domains, conflicts, validate_schedule
from clinicflow.models import Value


def test_domains_respect_unary_constraints(small):
    doms = build_domains(small)
    for appt in small.appointments:
        for v in doms[appt.id]:
            doc, room = small.doctor_by_id[v.doctor], small.room_by_id[v.room]
            assert doc.specialty == appt.specialty
            assert v.slot in doc.available_slots and v.slot in appt.allowed_slots
            assert set(appt.required_equipment) <= set(room.equipment)


def test_ecg_patient_only_gets_ecg_room_and_cardiologist(small):
    doms = build_domains(small)
    assert doms["A01"] and all(v.room == "R2" and v.doctor == "D2" for v in doms["A01"])


def test_conflicts_detects_double_booking(small):
    a, b = small.appointments[0], small.appointments[1]
    assert conflicts(a, Value("D2", "R2", 2), b, Value("D2", "R1", 2))  # same doctor
    assert conflicts(a, Value("D2", "R2", 2), b, Value("D1", "R2", 2))  # same room
    assert not conflicts(a, Value("D2", "R2", 2), b, Value("D2", "R2", 3))  # different slot


def test_same_patient_cannot_be_in_two_places(small):
    a03 = next(a for a in small.appointments if a.id == "A03")
    a08 = next(a for a in small.appointments if a.id == "A08")
    assert a03.patient == a08.patient == "Keller"
    assert conflicts(a03, Value("D1", "R1", 3), a08, Value("D4", "R3", 3))


def test_validator_flags_violations(small):
    bad = {a.id: Value("D1", "R1", 0) for a in small.appointments}
    errors = validate_schedule(small, bad)
    assert any("double-booked" in e for e in errors)
    assert any("needs cardiology" in e for e in errors)
    assert any("lacks" in e for e in errors)


def test_validator_flags_missing_assignment(small):
    assert any("unassigned" in e for e in validate_schedule(small, {}))
