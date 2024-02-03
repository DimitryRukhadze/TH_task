from datetime import date

from dateutil.relativedelta import relativedelta

from .models import CW, BaseModel, Requirements, Task


def get_prev_cw(task: Task) -> CW | None:
    active_cws = CW.objects.filter(task=task).order_by("-perform_date")[:2]
    if len(active_cws) > 1:
        return active_cws[1]
    return


def check_adjustment(latest_cw: CW, prev_cw: CW) -> bool:
    if prev_cw and prev_cw.next_due_date:
        return prev_cw.next_due_date != latest_cw.perform_date
    return False


def cnt_adjustment(latest_cw, expected_perf_date) -> int:

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


def check_tol_window(req: Requirements, latest_cw: CW, prev_cw: CW) -> bool:
    if req.due_months_unit:
        late, early = get_mos_tol_window(prev_cw.next_due_date, req)
        return early <= latest_cw.perform_date <= late
    return


def cnt_next_due(task_id: int) -> None:
    task = Task.objects.active().get(pk=task_id)
    curr_req = task.curr_requirements
    latest_cw = task.compliance
    prev_cw = get_prev_cw(task)

    if not latest_cw:
        return

    if not curr_req or not curr_req.due_months or curr_req.due_months == 0:
        latest_cw.next_due_date = None
        latest_cw.adj_mos = None
        latest_cw.save()

        return

    adjusted = False
    count_from = latest_cw.perform_date

    if latest_cw.adj_mos:
        adjusted = True

    if check_adjustment(latest_cw, prev_cw) and check_tol_window(curr_req, latest_cw, prev_cw):
        count_from = prev_cw.next_due_date
        adjusted = True


    if curr_req.due_months_unit == 'M':
        latest_cw.next_due_date = count_from + relativedelta(months=curr_req.due_months)

    elif curr_req.due_months_unit == 'D':
        latest_cw.next_due_date = count_from + relativedelta(days=curr_req.due_months)

    latest_cw.save()

    if adjusted:
        cnt_adjustment(latest_cw, count_from)
