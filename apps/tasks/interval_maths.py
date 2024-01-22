from math import ceil, floor
from dateutil.relativedelta import relativedelta
from datetime import date

from .models import Task, CW, Requirements


def cnt_next_due(task_id: int) -> None:
    task = Task.objects.get(pk=task_id)
    active_requirements = task.curr_requirements

    if not active_requirements.due_months:
        return

    cw = task.compliance

    if cw:
        if cw.adjusted_days:
            prev_cw = CW.objects.active().filter(
                    task=task
                ).order_by('-perform_date')[1]

            cw.next_due_date = prev_cw.next_due_date + relativedelta(
                    months=active_requirements.due_months
                )
        else:
            cw.next_due_date = cw.perform_date + relativedelta(
                    months=active_requirements.due_months
                )

        cw.save()


def check_adjustment(task: Task, perform_date) -> bool:
    latest_cw = task.compliance

    if latest_cw and latest_cw.next_due_date:
        return latest_cw.next_due_date != perform_date
    return False


def count_adjustment(task: Task, perf_date):
    delta = perf_date - task.compliance.next_due_date
    return delta.days


def cnt_mos_span_days(tol: Requirements, late_cw: CW) -> tuple:
    if tol.pos_tol_mos:
        pos_tol_days = relativedelta(days=tol.pos_tol_mos)
        pos_span = late_cw.next_due_date + pos_tol_days
    else:
        pos_span = late_cw.next_due_date

    if tol.neg_tol_mos:
        neg_tol_days = relativedelta(days=tol.neg_tol_mos)
        neg_span = late_cw.next_due_date + neg_tol_days
    else:
        neg_span = late_cw.next_due_date

    return neg_span, pos_span


def cnt_mos_span_months(tol: Requirements, late_cw: CW) -> tuple:
    if tol.pos_tol_mos:
        add_months = int(tol.pos_tol_mos)

        if tol.pos_tol_mos % int(tol.pos_tol_mos):
            add_days = ceil(30.5 / (tol.pos_tol_mos % int(tol.pos_tol_mos)))
        else:
            add_days = 0

        pos_tol_months = relativedelta(days=ceil(add_days), months=add_months)
        pos_span = late_cw.next_due_date + pos_tol_months

    else:
        pos_span = late_cw.next_due_date

    if tol.neg_tol_mos:
        sub_months = int(tol.neg_tol_mos)

        if tol.neg_tol_mos % int(tol.neg_tol_mos):
            sub_days = ceil(30.5 / (tol.neg_tol_mos % int(tol.neg_tol_mos)))
        else:
            sub_days = 0
        neg_tol_months = relativedelta(days=sub_days, months=sub_months)
        neg_span = late_cw.next_due_date + neg_tol_months
    else:
        neg_span = late_cw.next_due_date

    return neg_span, pos_span


def cnt_mos_span_percents(
            tol: Requirements,
            late_cw: CW,
        ) -> tuple:

    due_days = tol.due_months * 30.5

    if tol.pos_tol_mos:
        pos_days = ceil(due_days * (tol.pos_tol_mos / 100))
        pos_span = late_cw.next_due_date + relativedelta(days=pos_days)
    else:
        pos_span = late_cw.next_due_date

    if tol.neg_tol_mos:
        neg_days = floor(due_days * (tol.neg_tol_mos / 100))
        neg_span = late_cw.next_due_date + relativedelta(days=neg_days)
    else:
        neg_span = late_cw.next_due_date

    return neg_span, pos_span


def get_mos_span(task: Task) -> date | None:
    tolerance = task.curr_requirements
    latest_cw = task.compliance

    if latest_cw:
        if tolerance.mos_unit == 'M':
            return cnt_mos_span_months(tolerance, latest_cw)
        if tolerance.mos_unit == 'D':
            return cnt_mos_span_days(tolerance, latest_cw)
        if tolerance.mos_unit == 'P':
            return cnt_mos_span_percents(tolerance, latest_cw)
