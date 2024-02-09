from config.celery import app

from .interval_maths import cnt_next_due


@app.task
def update_next_due_date(task_id: int) -> None:
    cnt_next_due(task_id)
