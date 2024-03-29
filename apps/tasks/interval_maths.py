from math import ceil, floor
from dateutil.relativedelta import relativedelta
from datetime import date

from .models import Task, CW, Requirements


def cnt_next_due(task_id: int) -> None:
    task = Task.objects.get(pk=task_id)
    active_requirements = task.curr_requirements

    if not active_requirements:
        return

    if not active_requirements.due_months and not active_requirements.due_hrs and not active_requirements.due_cycles:
        return

    cw = task.compliance
    if cw:
        if active_requirements.due_hrs:
            if cw.adjusted_hrs:
                prev_cw = CW.objects.active().filter(
                        task=task
                    ).order_by('-perform_date')[1]
                cw.next_due_hrs = round(
                    prev_cw.perform_hours + active_requirements.due_hrs,
                    2
                )

            else:
                cw.next_due_hrs = round(
                    cw.perform_hours + active_requirements.due_hrs,
                    2
                )

        if active_requirements.due_cycles:
            if cw.adjusted_cycles:
                prev_cw = CW.objects.active().filter(
                        task=task
                    ).order_by('-perform_date')[1]
                cw.next_due_cycles = round(
                    prev_cw.perform_cycles + active_requirements.due_cycles,
                    2
                )

            else:
                cw.next_due_cycles = round(
                    cw.perform_cycles + active_requirements.due_cycles,
                    2
                )

        if active_requirements.due_months:
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


def check_adjustment(task: Task, payload: dict) -> bool:
    latest_cw = task.compliance

    if latest_cw and latest_cw.next_due_date:
        return latest_cw.next_due_date != payload["perform_date"]
    if latest_cw and latest_cw.next_due_hrs:
        return latest_cw.next_due_hrs != payload["perform_hours"]
    if latest_cw and latest_cw.next_due_cycles:
        return latest_cw.next_due_cycles != payload["perform_cycles"]
    return False


def count_mos_adjustment(task: Task, payload: dict):
    if payload.get("perform_date") and task.compliance.next_due_date:
        delta = payload["perform_date"] - task.compliance.next_due_date
        return delta.days


def count_hrs_adjustment(task: Task, payload: dict):
    if payload.get("perform_hours") and task.compliance.next_due_hrs:
        delta = payload["perform_hours"] - task.compliance.next_due_hrs
        return round(delta, 2)


def count_afl_adjustment(task: Task, payload: dict):
    if payload.get("perform_cycles") and task.compliance.next_due_cycles:
        delta = payload["perform_cycles"] - task.compliance.next_due_cycles
        return round(delta, 2)


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


def cnt_mos_span_percents(tol: Requirements, late_cw: CW) -> tuple:

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


def cnt_hrs_span_hours(tol: Requirements, cw: CW) -> tuple:

    if tol.pos_tol_hrs:
        pos_span = cw.next_due_hrs + tol.pos_tol_hrs
    else:
        pos_span = cw.next_due_hrs

    if tol.neg_tol_hrs:
        neg_span = cw.next_due_hrs + tol.neg_tol_hrs

    else:
        neg_span = cw.next_due_hrs

    return neg_span, pos_span


def cnt_hrs_span_percents(tol: Requirements, cw: CW) -> tuple:
    if tol.pos_tol_hrs:
        pos_hrs = tol.due_hrs * (tol.pos_tol_hrs / 100)
        pos_span = cw.next_due_hrs + pos_hrs
    else:
        pos_span = cw.next_due_hrs
    if tol.neg_tol_hrs:
        neg_hrs = tol.due_hrs * (tol.neg_tol_hrs / 100)
        neg_span = cw.next_due_hrs + neg_hrs
    else:
        neg_span = cw.next_due_hrs
    return neg_span, pos_span


def cnt_afl_span_cycles(tol: Requirements, cw: CW) -> tuple:
    if tol.pos_tol_afl:
        pos_span = cw.next_due_cycles + tol.pos_tol_afl
    else:
        pos_span = cw.next_due_cycles
    if tol.neg_tol_afl:
        neg_span = cw.next_due_cycles + tol.neg_tol_afl
    else:
        neg_span = cw.next_due_cycles

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


def get_hrs_span(task: Task) -> float | None:
    tolerance = task.curr_requirements
    latest_cw = task.compliance

    if latest_cw:
        if tolerance.hrs_unit == 'H':
            return cnt_hrs_span_hours(tolerance, latest_cw)
        if tolerance.hrs_unit == 'P':
            return cnt_hrs_span_percents(tolerance, latest_cw)


def get_afl_span(task: Task) -> float | None:
    tolerance = task.curr_requirements
    latest_cw = task.compliance

    if latest_cw:
        if tolerance.afl_unit == 'C':
            return cnt_afl_span_cycles(tolerance, latest_cw)
