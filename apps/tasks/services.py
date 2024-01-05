from .models import Task, CW
from api.schemas import TaskIn


def create_task(payload: TaskIn) -> Task:
    return Task.objects.create(**payload)


def update_task(task: Task, payload: TaskIn) -> Task:
    # TODO: подумать, что будет происходить, если мы меняем интервал
    task.code = payload.code
    task.description = payload.description
    task.due_months = payload.due_month
    task.save()
    return task


def delete_task():
    pass


def create_cw():
    # TODO: Проверить, что выводится ошибка создания, 
    # если дата нового CW больше последнего (при его наличии)
    pass


def delete_last_cw():
    pass