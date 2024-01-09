from datetime import date
from ninja import Schema


class TaskOut(Schema):
    pk: int
    code: str
    description: str
    due_months: int | None = None


class TaskIn(Schema):
    code: str
    description: str
    due_months: int = None


class ComplianceOut(Schema):
    pk: int
    task: TaskOut
    perform_date: date
    next_due_date: date | None = None


class ComplianceIn(Schema):
    perform_date: date
    next_due_date: date = None
