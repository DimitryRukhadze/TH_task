from dateutil.relativedelta import relativedelta
from datetime import date

from .models import Task, BaseModel, CW, Requirements


def get_prev_cw(task: Task) -> CW | None:
    active_cws = CW.objects.filter(task=task).order_by("-perform_date")
    if len(active_cws) > 1:
        return active_cws[1]
    return


def check_adjustment(latest_cw: CW, prev_cw: CW) -> bool:
    if prev_cw and prev_cw.next_due_date:
        return prev_cw.next_due_date != latest_cw.perform_date
    return False


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
    task = BaseModel.get_object_or_404(Task, pk=task_id)
    curr_req = task.curr_requirements
    latest_cw = task.compliance
    prev_cw = get_prev_cw(task)

    if not curr_req or not latest_cw:
        return

    count_from = latest_cw.perform_date

    if check_adjustment(latest_cw, prev_cw) and check_tol_window(curr_req, latest_cw, prev_cw):
        count_from = prev_cw.next_due_date

    if curr_req.due_months_unit == 'M':
        latest_cw.next_due_date = count_from + relativedelta(months=curr_req.due_months)

    if curr_req.due_months_unit == 'D':
        latest_cw.next_due_date = count_from + relativedelta(days=curr_req.due_months)

    latest_cw.save()
