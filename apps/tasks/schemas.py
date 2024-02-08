from datetime import date
from ninja import Schema


class TaskIn(Schema):
    code: str
    description: str


class ComplianceOut(Schema):
    pk: int
    perform_date: date
    perform_hrs: float | None
    perform_cyc: int | None
    next_due_date: date | None
    next_due_hrs: float | None
    next_due_cyc: int | None
    adj_mos: int | None
    adj_hrs: float | None


class ComplianceIn(Schema):
    perform_date: date
    perform_hrs: float | None = None
    perform_cyc: int | None = None


class ReqIn(Schema):
    is_active: bool
    due_months: int | None = None
    due_months_unit: str | None = None
    due_hrs: float | None = None
    due_cyc: int | None = None
    tol_pos_mos: float | None = None
    tol_neg_mos: float | None = None
    tol_mos_unit: str | None = None
    tol_pos_hrs: float | None = None
    tol_neg_hrs: float | None = None
    tol_hrs_unit: str | None = None
    tol_pos_cyc: float | None = None
    tol_neg_cyc: float | None = None
    tol_cyc_unit: str | None = None


class ReqOut(Schema):
    pk: int
    is_active: bool
    due_months: int | None = None
    due_months_unit: str | None = None
    due_hrs: float | None = None
    due_cyc: int | None = None
    tol_pos_mos: float | None = None
    tol_neg_mos: float | None = None
    tol_mos_unit: str | None = None
    tol_pos_hrs: float | None = None
    tol_neg_hrs: float | None = None
    tol_hrs_unit: str | None = None
    tol_pos_cyc: float | None = None
    tol_neg_cyc: float | None = None
    tol_cyc_unit: str | None = None


class ListTaskOut(Schema):
    pk: int
    code: str
    description: str
    compliance: ComplianceOut | None = None
    requirement: ReqOut | None = None

    @staticmethod
    def resolve_compliance(obj):
        if not obj.compliance_qs:
            return
        return obj.compliance_qs[0]

    @staticmethod
    def resolve_requirement(obj):
        if not obj.requirement_qs:
            return
        return obj.requirement_qs[0]


class TaskOut(Schema):
    code: str
    description: str
    compliances: list[ComplianceOut] | None = None
    requirements: list[ReqOut] | None = None

    @staticmethod
    def resolve_compliances(obj):
        return obj.compliances.active().order_by("-perform_date")[:5]


class Error(Schema):
    message: str
