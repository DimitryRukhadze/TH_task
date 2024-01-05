from datetime import date

from ninja import Schema


class ComplianceIn(Schema):
    perform_date: date


class ComplianceOut(Schema):
    pk: int
    perform_date: date
    next_due_date: date = None


class TaskOut(Schema):
    pk: int
    code: str
    description: str
    due_month: int = None
    compliance: ComplianceOut = None


class TaskIn(Schema):
    code: str
    description: str
    due_month: int = None
