"""Regenerate the medium/large instances deterministically."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from clinicflow.generator import generate  # noqa: E402
from clinicflow.models import save_instance  # noqa: E402

DATA = Path(__file__).resolve().parents[1] / "data"

if __name__ == "__main__":
    save_instance(generate(20, 5, 4, 16, seed=1, tightness=0.5, name="medium_case"), DATA / "medium_case.json")
    save_instance(generate(40, 6, 5, 16, seed=7, tightness=0.5, name="large_case"), DATA / "large_case.json")
    print("wrote medium_case.json, large_case.json")
