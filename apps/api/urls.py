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
    return get_object_or_404(Task, pk=task_id)


@api.post("tasks", response=list[TaskOut])
def create_tasks(request, payload: list[TaskIn]):
    new_objs = [Task(**fields.dict()) for fields in payload]
    new_tasks = Task.objects.bulk_create(new_objs)
    return new_tasks


@api.put("tasks/{task_id}", response=TaskOut)
def update_tasks(request, task_id: int, payload: TaskIn):
    update_obj = get_object_or_404(Task, pk=task_id)

    for key, value in payload.dict().items():
        setattr(update_obj, key, value)

    update_obj.save()

    return update_obj


urlpatterns = [
    path("", api.urls),
]
