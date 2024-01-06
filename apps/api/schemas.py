from datetime import date
from ninja import Schema


class TaskOut(Schema):
    pk: int
    code: str
    description: str
    due_month: int = None


class TaskIn(Schema):
    code: str
    description: str
    due_month: int = None


class ComplianceOut(Schema):
    pk: int
    task: int
    perform_date: date
    next_due_date: date = None


class ComplianceIn(Schema):
    task: int
    perform_date: date
    next_due_date: date = None
