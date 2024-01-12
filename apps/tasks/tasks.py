from config.celery import app

from .services import cnt_next_due, get_tasks


@app.task
def update_next_due_date(task_id: int) -> None:
    cnt_next_due(task_id)


@app.task
def update_daily_due_dates():
    tasks = get_tasks()
    for task in tasks:
        cnt_next_due(task.pk)
    print('Due dates updated')
