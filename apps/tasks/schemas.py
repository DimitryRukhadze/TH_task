from datetime import date
from ninja import Schema

from .models import Task


class TaskOut(Schema):
    pk: int
    code: str
    description: str
    due_months: int | None = None
    next_due_date: date | None = None

    @staticmethod
    def resolve_next_due_date(obj: Task) -> date | None:
        if obj.compliance:
            return obj.compliance.next_due_date
        return


class TaskIn(Schema):
    code: str
    description: str
    due_months: int = None


class ComplianceOut(Schema):
    pk: int
    task: TaskOut
    perform_date: date
    perform_hours: float | None = None
    perform_cycles: float | None = None
    next_due_date: date | None = None
    next_due_hrs: float | None = None
    next_due_cycles: float | None = None


class ComplianceIn(Schema):
    perform_date: date
    next_due_date: date | None = None
    perform_hours: float | None = None
    next_due_hrs: float | None = None
    perform_cycles: float | None = None
    next_due_cycles: float | None = None


class ReqIn(Schema):
    task: TaskOut | None = None
    mos_unit: str = None
    hrs_unit: str = None
    afl_unit: str = None
    due_months: int | None = None
    due_hrs: float | None = None
    due_cycles: float | None = None
    pos_tol_mos: float | None = None
    neg_tol_mos: float | None = None
    pos_tol_hrs: float | None = None
    neg_tol_hrs: float | None = None
    pos_tol_afl: float | None = None
    neg_tol_afl: float | None = None
    is_active: bool = None


class ReqOut(Schema):
    pk: int
    task: TaskOut
    mos_unit: str
    hrs_unit: str
    afl_unit: str
    due_months: int | None
    due_hrs: float | None
    due_cycles: float | None
    pos_tol_mos: float | None
    neg_tol_mos: float | None
    pos_tol_hrs: float | None
    neg_tol_hrs: float | None
    pos_tol_afl: float | None
    neg_tol_afl: float | None
    is_active: bool


class Error(Schema):
    message: str
