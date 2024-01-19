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
    next_due_date: date | None = None


class ComplianceIn(Schema):
    perform_date: date
    next_due_date: date | None = None


class Error(Schema):
    message: str
