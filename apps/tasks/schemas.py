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
    curr_requirements: ReqOut | None = None

    @staticmethod
    def resolve_compliance(obj):
        if not obj.compliance:
            return
        return obj.compliance


class TaskOut(Schema):
    class Meta:
        fields = [
            "pk",
            "code",
            "description",
            "all_compliances",
            "all_requirements"
            ]

    pk: int
    code: str
    description: str
    all_compliances: list[ComplianceOut] | None = None
    all_requirements: list[ReqOut] | None = None


class Error(Schema):
    message: str
