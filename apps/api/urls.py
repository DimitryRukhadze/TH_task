from django.urls import path
from django.shortcuts import get_object_or_404
from ninja import NinjaAPI, Schema
from typing import List

from apps.tasks.models import Task


api = NinjaAPI()


class TaskOut(Schema):
    pk: int
    code: str
    description: str
    due_month: int = None


@api.get("tasks", response=List[TaskOut])
def get_all_tasks(request):
    tasks_queryset = Task.objects.active()
    return tasks_queryset


@api.get("tasks/{task_id}", response=TaskOut)
def get_task(request, task_id: int):
    task = get_object_or_404(Task, id=task_id)
    return task


urlpatterns = [
    path("", api.urls),
]
