from config.celery import app

from .interval_maths import cnt_next_due, cnt_adjustment
from .models import Task


@app.task
def update_next_due_date(task_id: int) -> None:
    cnt_next_due(task_id)


@app.task
def update_daily_due_dates():
    tasks = Task.objects.active().order_by("code", "description")
    for task in tasks:
        cnt_next_due(task.pk)
    print('Due dates updated')
