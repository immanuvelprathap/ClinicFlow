"""ClinicFlow: clinic appointment scheduling as a Constraint Satisfaction Problem."""

from clinicflow.models import Instance, load_instance
from clinicflow.csp import build_domains, validate_schedule
from clinicflow.solvers import SOLVERS, solve

__all__ = ["Instance", "load_instance", "build_domains", "validate_schedule", "SOLVERS", "solve"]
