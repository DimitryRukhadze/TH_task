from datetime import date
from ninja import Schema


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


class ReqIn(Schema):
    is_active: bool
    due_months: int = None
    due_months_unit: str | None = None
    tol_pos_mos: float | None = None
    tol_neg_mos: float | None = None
    tol_mos_unit: str | None = None


class ReqOut(Schema):
    pk: int
    is_active: bool
    due_months: int | None = None
    due_months_unit: str | None = None
    tol_pos_mos: float | None = None
    tol_neg_mos: float | None = None
    tol_mos_unit: str | None = None


class ListTaskOut(Schema):
    pk: int
    code: str
    description: str
    compliance: ComplianceOut | None = None
    requirements: ReqOut | None = None

    @staticmethod
    def resolve_compliance(obj):
        if not obj.last_compliances:
            return
        return obj.last_compliances[0]

    @staticmethod
    def resolve_requirements(obj):
        if not obj.active_requirements:
            return
        return obj.active_requirements[0]


class TaskOut(Schema):
    code: str
    description: str
    task_compliances: list[ComplianceOut] | None = None
    task_requirements: list[ReqOut] | None = None

    @staticmethod
    def resolve_task_compliances(obj):
        if not obj.cws:
            return
        return obj.cws

    @staticmethod
    def resolve_task_requirements(obj):
        if not obj.all_reqs:
            return
        return obj.all_reqs


class Error(Schema):
    message: str
