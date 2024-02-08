from datetime import date
from decimal import Decimal

from dateutil.relativedelta import relativedelta

from .models import CW, Requirements, Task


def get_prev_cw(task: Task) -> CW | None:
    active_cws = CW.objects.active().filter(task=task).order_by("-perform_date")[:2]
    if len(active_cws) > 1:
        return active_cws[1]
    return


def cnt_mos_adjustment(latest_cw, expected_perf_date):

    expected_interval = latest_cw.next_due_date - expected_perf_date
    fact_interval = latest_cw.next_due_date - latest_cw.perform_date
    adj = fact_interval - expected_interval

    latest_cw.adj_mos = adj.days
    latest_cw.save()


def cnt_hrs_adjustment(latest_cw, expected_perf_hrs):

    expected_interval = latest_cw.next_due_hrs - expected_perf_hrs
    fact_interval = latest_cw.next_due_hrs - latest_cw.perform_hrs
    latest_cw.adj_hrs = fact_interval - expected_interval
    latest_cw.save()


def cnt_cyc_adjustment(latest_cw, expected_perf_cyc):
    expected_interval = latest_cw.next_due_cyc - expected_perf_cyc
    fact_interval = latest_cw.next_due_cyc - latest_cw.perform_cyc
    latest_cw.adj_cyc = fact_interval - expected_interval
    latest_cw.save()


def get_mos_tol_window(mid_date: date, req: Requirements) -> tuple:

    days_in_month = 30.5

    if req.tol_pos_mos and req.tol_mos_unit == 'M':
        tol_pos = mid_date + relativedelta(months=int(req.tol_pos_mos))
    elif req.tol_pos_mos and req.tol_mos_unit == 'D':
        tol_pos = mid_date + relativedelta(days=int(req.tol_pos_mos))
    elif req.tol_pos_mos and req.tol_mos_unit == 'P':
        due_days = req.due_months * days_in_month
        act_days = due_days * (float(req.tol_pos_mos) / 100)
        tol_pos = mid_date + relativedelta(days=round(act_days, 2))
    else:
        tol_pos = mid_date

    if req.tol_neg_mos and req.tol_mos_unit == 'M':
        tol_neg = mid_date - relativedelta(months=int(req.tol_neg_mos))
    elif req.tol_neg_mos and req.tol_mos_unit == 'D':
        tol_neg = mid_date - relativedelta(days=int(req.tol_neg_mos))
    elif req.tol_neg_mos and req.tol_mos_unit == 'P':
        due_days = req.due_months * days_in_month
        act_days = due_days * (float(req.tol_neg_mos) / 100)
        tol_neg = mid_date - relativedelta(days=round(act_days, 2))
    else:
        tol_neg = mid_date

    return tol_pos, tol_neg


def check_mos_tol_window(req: Requirements, latest_cw: CW, prev_cw: CW) -> bool:
    if req.due_months_unit:
        late, early = get_mos_tol_window(prev_cw.next_due_date, req)
        return early <= latest_cw.perform_date <= late
    return


def get_hrs_tol_window(mid_hrs: Decimal, req: Requirements) -> tuple:

    if req.tol_pos_hrs:
        if req.tol_hrs_unit == "P":
            pos_hrs = req.due_hrs * (req.tol_pos_hrs / 100)
        else:
            pos_hrs = req.tol_pos_hrs

        tol_pos = mid_hrs + pos_hrs
    else:
        tol_pos = mid_hrs

    if req.tol_neg_hrs:
        if req.tol_hrs_unit == "P":
            neg_hrs = req.due_hrs * (req.tol_neg_hrs / 100)
        else:
            neg_hrs = req.tol_neg_hrs

        tol_neg = mid_hrs - neg_hrs
    else:
        tol_neg = mid_hrs

    return tol_pos, tol_neg


def check_hrs_tol_window(req: Requirements, latest_cw: CW, prev_cw: CW) -> bool:
    if req.due_hrs:
        late, early = get_hrs_tol_window(prev_cw.next_due_hrs, req)
        return early <= latest_cw.perform_hrs <= late
    return


def get_cyc_tol_window(mid_cyc: Decimal, req: Requirements) -> tuple:

    if req.tol_pos_cyc:
        if req.tol_cyc_unit == "P":
            pos_cyc = round(req.due_cyc * (req.tol_pos_cyc / 100))
        else:
            pos_cyc = req.tol_pos_cyc

        tol_pos = mid_cyc + pos_cyc

    else:
        tol_pos = mid_cyc

    if req.tol_neg_cyc:
        if req.tol_cyc_unit == "P":
            neg_cyc = round(req.due_cyc * (req.tol_pos_cyc / 100))
        else:
            neg_cyc = req.tol_neg_cyc

        tol_neg = mid_cyc - neg_cyc

    else:
        tol_neg = mid_cyc

    return tol_pos, tol_neg


def check_cyc_tol_window(req: Requirements, latest_cw: CW, prev_cw: CW) -> bool:
    if req.due_cyc:
        late, early = get_cyc_tol_window(prev_cw.next_due_cyc, req)
        return early <= latest_cw.perform_cyc <= late
    return


def check_adjustment_exists(latest_cw: CW, prev_cw: CW, axis: str) -> bool:

    if axis == "MOS" and prev_cw and prev_cw.next_due_date:
        return prev_cw.next_due_date != latest_cw.perform_date

    if axis == "HRS" and prev_cw and prev_cw.next_due_hrs:
        return prev_cw.next_due_hrs != latest_cw.perform_hrs

    if axis == "CYC" and prev_cw and prev_cw.next_due_cyc:
        return prev_cw.next_due_cyc != latest_cw.perform_cyc

    return


def cnt_mos_due(req: Requirements, latest_cw: CW, prev_cw: CW) -> None:
    if not req.due_months or req.due_months == 0:
        latest_cw.next_due_date = None
        latest_cw.adj_mos = None
        latest_cw.save()
        return

    count_from_date = latest_cw.perform_date
    is_adjusted = False

    if check_adjustment_exists(latest_cw, prev_cw, "MOS") and check_mos_tol_window(req, latest_cw, prev_cw):
        count_from_date = prev_cw.next_due_date
        is_adjusted = True

    if req.due_months_unit == 'M':
        latest_cw.next_due_date = count_from_date + relativedelta(months=req.due_months)

    elif req.due_months_unit == 'D':
        latest_cw.next_due_date = count_from_date + relativedelta(days=req.due_months)

    latest_cw.save()

    if is_adjusted or latest_cw.adj_mos:
        cnt_mos_adjustment(latest_cw, count_from_date)


def cnt_hrs_due(req: Requirements, latest_cw: CW, prev_cw: CW) -> None:
    if not req.due_hrs or req.due_hrs == 0:
        latest_cw.next_due_hrs = None
        latest_cw.adj_hrs = None
        latest_cw.save()
        return

    count_from_hrs = latest_cw.perform_hrs
    is_adjusted = False

    if check_adjustment_exists(latest_cw, prev_cw, "HRS") and check_hrs_tol_window(req, latest_cw, prev_cw):
        count_from_hrs = prev_cw.next_due_hrs
        is_adjusted = True

    latest_cw.next_due_hrs = count_from_hrs + req.due_hrs
    latest_cw.save()

    if is_adjusted or latest_cw.adj_hrs:
        cnt_hrs_adjustment(latest_cw, count_from_hrs)


def cnt_cyc_due(req: Requirements, latest_cw: CW, prev_cw: CW) -> None:
    if not req.due_cyc or req.due_cyc == 0:
        latest_cw.next_due_cyc = None
        latest_cw.adj_cyc = None
        latest_cw.save()
        return

    count_from_cyc = latest_cw.perform_cyc
    is_adjusted = False

    if check_adjustment_exists(latest_cw, prev_cw, "CYC") and check_cyc_tol_window(req, latest_cw, prev_cw):
        count_from_cyc = prev_cw.next_due_cyc
        is_adjusted = True

    latest_cw.next_due_cyc = count_from_cyc + req.due_cyc
    latest_cw.save()

    if is_adjusted or latest_cw.adj_cyc:
        cnt_cyc_adjustment(latest_cw, count_from_cyc)


def nullify_cw_dues(cw: CW) -> None:
    cw.next_due_date = None
    cw.next_due_hrs = None
    cw.next_due_cyc = None
    cw.adj_mos = None
    cw.adj_hrs = None
    cw.adj_cyc = None

    cw.save()


def cnt_next_due(task_id: int) -> None:
    task = Task.objects.active().get(pk=task_id)
    curr_req = task.curr_requirements
    latest_cw = task.compliance
    prev_cw = get_prev_cw(task)

    if not latest_cw:
        return

    if not curr_req:    # Нужно на случай update или delete requirements
        nullify_cw_dues(latest_cw)
        return

    cnt_mos_due(curr_req, latest_cw, prev_cw)
    cnt_hrs_due(curr_req, latest_cw, prev_cw)
    cnt_cyc_due(curr_req, latest_cw, prev_cw)
