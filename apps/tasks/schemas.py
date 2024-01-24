from datetime import date
from ninja import Schema


class TaskOut(Schema):
    pk: int
    code: str
    description: str


class TaskIn(Schema):
    code: str
    description: str


class ComplianceOut(Schema):
    pk: int
    perform_date: date
    next_due_date: date | None = None


class ComplianceIn(Schema):
    perform_date: date
    next_due_date: date | None = None


class ReqIn(Schema):
    is_active: bool
    due_months: float | None = None
    due_months_unit: str | None = None
    tol_pos_mos: float | None = None
    tol_neg_mos: float | None = None
    tol_mos_unit: str | None = None


class ReqOut(Schema):
    pk: int
    is_active: bool
    due_months: float | None = None
    due_months_unit: str | None = None
    tol_pos_mos: float | None = None
    tol_neg_mos: float | None = None
    tol_mos_unit: str | None = None


class Error(Schema):
    message: str
