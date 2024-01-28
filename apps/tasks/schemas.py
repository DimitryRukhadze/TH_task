from datetime import date
from ninja import Schema
from typing import Optional


class TaskIn(Schema):
    code: str
    description: str


class ComplianceOut(Schema):
    pk: int
    perform_date: date
    next_due_date: date | None = None
    adj_mos: int | None


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


class TaskOut(Schema):
    pk: int
    code: str
    description: str
    compliance: Optional[ComplianceOut] | None
    all_compliances: Optional[list[ComplianceOut]] = None
    all_requirements: Optional[list[ReqOut]] = None
    curr_requirements: ReqOut | None

    @staticmethod
    def resolve_compliance(obj):
        if obj.all_compliances:
            return

    @staticmethod
    def resolve_curr_requirements(obj):
        if obj.all_requirements:
            return


class Error(Schema):
    message: str
