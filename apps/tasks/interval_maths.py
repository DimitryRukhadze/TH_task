from dateutil.relativedelta import relativedelta

from .models import Task, BaseModel


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
        if not curr_req.due_months_unit:
            latest_cw.next_due_date = None

        latest_cw.save()


def check_adjustment(task: Task, perform_date) -> bool:
    latest_cw = task.compliance

    if latest_cw and latest_cw.next_due_date:
        return latest_cw.next_due_date != perform_date
    return False
