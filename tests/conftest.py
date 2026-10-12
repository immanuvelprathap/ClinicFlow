from pathlib import Path

import pytest

from clinicflow.models import load_instance

DATA = Path(__file__).resolve().parents[1] / "data"


@pytest.fixture
def small():
    return load_instance(DATA / "small_case.json")


@pytest.fixture
def medium():
    return load_instance(DATA / "medium_case.json")


@pytest.fixture
def impossible():
    return load_instance(DATA / "impossible_case.json")
