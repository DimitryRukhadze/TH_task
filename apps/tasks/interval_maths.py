from .models import Task, CW

from dateutil.relativedelta import relativedelta


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