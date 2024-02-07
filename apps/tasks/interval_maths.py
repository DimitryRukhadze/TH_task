from datetime import date

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


def get_hrs_tol_window(mid_hrs, req: Requirements) -> tuple:
    mid_hrs = float(mid_hrs)

    if req.tol_pos_hrs:
        pos_hrs = float(req.tol_pos_hrs)

        if req.tol_hrs_unit == "P":
            pos_hrs = float(req.due_hrs) * (float(req.tol_pos_hrs) / 100)

        tol_pos = mid_hrs + pos_hrs
    else:
        tol_pos = mid_hrs

    if req.tol_neg_hrs:
        neg_hrs = float(req.tol_neg_hrs)

        if req.tol_hrs_unit == "P":
            neg_hrs = float(req.due_hrs) * (float(req.tol_neg_hrs) / 100)

        tol_neg = mid_hrs - neg_hrs
    else:
        tol_neg = mid_hrs

    return tol_pos, tol_neg


def check_hrs_tol_window(req: Requirements, latest_cw: CW, prev_cw: CW) -> bool:
    if req.due_hrs:
        late, early = get_hrs_tol_window(prev_cw.next_due_hrs, req)
        return early <= latest_cw.perform_hrs <= late
    return


def check_adjustment(latest_cw: CW, prev_cw: CW, mos: bool = False, hrs: bool = False) -> bool:

    if mos and prev_cw and prev_cw.next_due_date:
        return prev_cw.next_due_date != latest_cw.perform_date

    if hrs and prev_cw and prev_cw.next_due_hrs:
        return prev_cw.next_due_hrs != latest_cw.perform_hrs
    return


def cnt_mos_due(req: Requirements, latest_cw: CW, prev_cw: CW) -> None:
    if not req.due_months or req.due_months == 0:
        latest_cw.next_due_date = None
        latest_cw.adj_mos = None
        latest_cw.save()
        return

    count_from_date = latest_cw.perform_date
    is_adjusted = False

    if check_adjustment(latest_cw, prev_cw, mos=True) and check_mos_tol_window(req, latest_cw, prev_cw):
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

    if check_adjustment(latest_cw, prev_cw, hrs=True) and check_hrs_tol_window(req, latest_cw, prev_cw):
        count_from_hrs = prev_cw.next_due_hrs
        is_adjusted = True

    latest_cw.next_due_hrs = count_from_hrs + req.due_hrs
    latest_cw.save()

    if is_adjusted or latest_cw.adj_hrs:
        cnt_hrs_adjustment(latest_cw, count_from_hrs)


def cnt_next_due(task_id: int) -> None:
    task = Task.objects.active().get(pk=task_id)
    curr_req = task.curr_requirements
    latest_cw = task.compliance
    prev_cw = get_prev_cw(task)

    if not latest_cw:
        return

    if not curr_req:
        latest_cw.next_due_date = None
        latest_cw.next_due_hrs = None
        latest_cw.adj_mos = None
        latest_cw.adj_hrs = None

        latest_cw.save()

        return

    cnt_mos_due(curr_req, latest_cw, prev_cw)
    cnt_hrs_due(curr_req, latest_cw, prev_cw)

#    count_from_hrs = latest_cw.perform_hrs
#
#    if adjusted_axes["HRS"] and check_hrs_tol_window(curr_req, latest_cw, prev_cw):
#        count_from_hrs = prev_cw.next_due_hrs
#
#    if curr_req.due_months_unit == 'M':
#        latest_cw.next_due_date = count_from_date + relativedelta(months=curr_req.due_months)
#
#    elif curr_req.due_months_unit == 'D':
#        latest_cw.next_due_date = count_from_date + relativedelta(days=curr_req.due_months)
#
#    if curr_req.due_hrs:
#        latest_cw.next_due_hrs = count_from_hrs + curr_req.due_hrs
#
#    latest_cw.save()
#
#    if adjusted_axes["MOS"] or latest_cw.adj_mos:
#        cnt_mos_adjustment(latest_cw, count_from_date)
#
#    if adjusted_axes["HRS"] or latest_cw.adj_hrs:
#        pass
