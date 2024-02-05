from datetime import date

from dateutil.relativedelta import relativedelta

from .models import CW, Requirements, Task


def get_prev_cw(task: Task) -> CW | None:
    active_cws = CW.objects.active().filter(task=task).order_by("-perform_date")[:2]
    if len(active_cws) > 1:
        return active_cws[1]
    return


def check_adjustment(latest_cw: CW, prev_cw: CW) -> dict:
    adjusted_axes = {
        "MOS": None,
        "HRS": None
    }

    if prev_cw and prev_cw.next_due_date:
        adjusted_axes["MOS"] = prev_cw.next_due_date != latest_cw.perform_date

    if prev_cw and prev_cw.next_due_hrs:
        adjusted_axes["HRS"] = prev_cw.next_due_hrs != latest_cw.perform_hrs

    return adjusted_axes


def cnt_mos_adjustment(latest_cw, expected_perf_date) -> int:

    expected_interval = latest_cw.next_due_date - expected_perf_date
    fact_interval = latest_cw.next_due_date - latest_cw.perform_date
    adj = fact_interval - expected_interval

    latest_cw.adj_mos = adj.days
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


def cnt_next_due(task_id: int) -> None:
    task = Task.objects.active().get(pk=task_id)
    curr_req = task.curr_requirements
    latest_cw = task.compliance
    prev_cw = get_prev_cw(task)

    if not latest_cw:
        return

#    if not curr_req or not curr_req.due_months or curr_req.due_months == 0:
#        latest_cw.next_due_date = None
#        latest_cw.adj_mos = None
#        latest_cw.save()

#        return
    if not curr_req:
        latest_cw.next_due_date = None
        latest_cw.next_due_hrs = None
        latest_cw.adj_mos = None
        latest_cw.adj_hrs = None

        latest_cw.save()

        return

    count_from_date = latest_cw.perform_date
    count_from_hrs = latest_cw.perform_hrs

    adjusted_axes = check_adjustment(latest_cw, prev_cw)

    if adjusted_axes["MOS"] and check_mos_tol_window(curr_req, latest_cw, prev_cw):
        count_from_date = prev_cw.next_due_date

    if adjusted_axes["HRS"] and check_hrs_tol_window(curr_req, latest_cw, prev_cw):
        count_from_hrs = prev_cw.next_due_hrs

    if curr_req.due_months_unit == 'M':
        latest_cw.next_due_date = count_from_date + relativedelta(months=curr_req.due_months)

    elif curr_req.due_months_unit == 'D':
        latest_cw.next_due_date = count_from_date + relativedelta(days=curr_req.due_months)

    if curr_req.due_hrs:
        latest_cw.next_due_hrs = count_from_hrs + curr_req.due_hrs

    latest_cw.save()

    if adjusted_axes["MOS"] or latest_cw.adj_mos:
        cnt_mos_adjustment(latest_cw, count_from_date)

#    if adjusted_axes["HRS"] or latest_cw.adj_hrs:
#        pass
