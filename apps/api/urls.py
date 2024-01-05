from typing import List

from django.shortcuts import get_object_or_404
from django.urls import path
from ninja import NinjaAPI

from apps.tasks.models import Task

from .schemas import TaskOut

api = NinjaAPI()

# Пишу тебе структуру endpoint-ов, у тебя пока каша судя по тестам
# /api/tasks/ - вывод всех тасков + POST на создание таска
# /api/tasks/{task_id}/ - RUD операции над таском
# /api/tasks/{task_id}/cws/ - вывод всех cw для таска + POST на создание нового CW
# /api/tasks/{task_id}/cws/{cw_id}/ - RUD операции над CW


@api.get("tasks/", response=list)
def get_all_tasks(requests):
    # добавил сортировку
    # TODO: Добавить пагинацию!
    return Task.objects.active().order_by("code", "description")
 

@api.get("tasks/{task_id}/", response=TaskOut)
def get_task(requests, task_id: int):
    return get_object_or_404(Task, id=task_id)


urlpatterns = [
    path("", api.urls),
]
