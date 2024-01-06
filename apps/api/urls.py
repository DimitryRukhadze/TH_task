from django.urls import path
from django.shortcuts import get_object_or_404
from ninja import NinjaAPI

from apps.tasks.models import Task
from .schemas import TaskIn, TaskOut, ComplianceIn, ComplianceOut


api = NinjaAPI()


@api.get("tasks", response=list[TaskOut])
def get_all_tasks(request):
    tasks_queryset = Task.objects.active()
    return tasks_queryset


@api.get("tasks/{task_id}", response=TaskOut)
def get_task(request, task_id: int):
    task = get_object_or_404(Task, pk=task_id)
    return task


urlpatterns = [
    path("", api.urls),
]
