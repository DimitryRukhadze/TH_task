from math import ceil, floor
from dateutil.relativedelta import relativedelta
from datetime import date

from .models import Task, CW, Requirements, BaseModel


def cnt_next_due(task_id: int) -> None:
    task = BaseModel.get_object_or_404(Task, pk=task_id)
    curr_req = task.curr_requirements
    latest_cw = task.compliance

    if task.curr_requirements and task.compliance:
        if curr_req.due_months_unit == 'M':
            months = curr_req.due_months
            latest_cw.next_due_date = latest_cw.perform_date + relativedelta(months=months)
        if curr_req.due_months_unit == 'D':
            days = curr_req.due_months
            latest_cw.next_due_date = latest_cw.perform_date + relativedelta(days=days)

        latest_cw.save()


def check_adjustment(task: Task, perform_date) -> bool:
    latest_cw = task.compliance

    if latest_cw and latest_cw.next_due_date:
        return latest_cw.next_due_date != perform_date
    return False


def cnt_tol_span_days(tol: Requirements, late_cw: CW) -> tuple:
    if tol.pos_tol:
        pos_tol_days = relativedelta(days=tol.pos_tol)
        pos_span = late_cw.next_due_date + pos_tol_days
    else:
        pos_span = late_cw.next_due_date

    if tol.neg_tol:
        neg_tol_days = relativedelta(days=tol.neg_tol)
        neg_span = late_cw.next_due_date + neg_tol_days
    else:
        neg_span = late_cw.next_due_date

    return neg_span, pos_span


def cnt_tol_span_months(tol: Requirements, late_cw: CW) -> tuple:
    if tol.pos_tol:
        add_months = int(tol.pos_tol)

        if tol.pos_tol % int(tol.pos_tol):
            add_days = ceil(30.5 / (tol.pos_tol % int(tol.pos_tol)))
        else:
            add_days = 0

        pos_tol_months = relativedelta(days=ceil(add_days), months=add_months)
        pos_span = late_cw.next_due_date + pos_tol_months

    else:
        pos_span = late_cw.next_due_date

    if tol.neg_tol:
        sub_months = int(tol.neg_tol)

        if tol.neg_tol % int(tol.neg_tol):
            sub_days = ceil(30.5 / (tol.neg_tol % int(tol.neg_tol)))
        else:
            sub_days = 0
        neg_tol_months = relativedelta(days=sub_days, months=sub_months)
        neg_span = late_cw.next_due_date + neg_tol_months
    else:
        neg_span = late_cw.next_due_date

    return neg_span, pos_span


def cnt_tol_span_percents(
            tol: Requirements,
            late_cw: CW,
            due_months: int | float
        ) -> tuple:

    due_days = due_months * 30.5

    if tol.pos_tol:
        pos_days = ceil(due_days * (tol.pos_tol / 100))
        pos_span = late_cw.next_due_date + relativedelta(days=pos_days)
    else:
        pos_span = late_cw.next_due_date

    if tol.neg_tol:
        neg_days = floor(due_days * (tol.neg_tol / 100))
        neg_span = late_cw.next_due_date + relativedelta(days=neg_days)
    else:
        neg_span = late_cw.next_due_date

    return neg_span, pos_span


def get_tolerance_span(task: Task) -> date | None:
    tolerance = task.curr_tolerance
    latest_cw = task.compliance

    if latest_cw:
        if tolerance.tol_type == 'M':
            return cnt_tol_span_months(tolerance, latest_cw)
        if tolerance.tol_type == 'D':
            return cnt_tol_span_days(tolerance, latest_cw)
        if tolerance.tol_type == 'P':
            return cnt_tol_span_percents(tolerance, latest_cw, task.due_months)
