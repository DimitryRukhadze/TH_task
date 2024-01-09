from django.urls import path
from django.shortcuts import get_object_or_404


from ninja import NinjaAPI

from .models import Task, CW, BaseModel
from .schemas import TaskIn, TaskOut, ComplianceIn, ComplianceOut


api = NinjaAPI()


@api.get("tasks/", response=list[TaskOut])
def get_all_tasks(request):
    tasks_queryset = Task.objects.active()
    return tasks_queryset


@api.get("tasks/{task_id}/", response=TaskOut)
def get_task(request, task_id: int):
    return get_object_or_404(Task, pk=task_id)


@api.post("tasks/", response=list[TaskOut])
def create_tasks(request, payload: list[TaskIn]):
    new_objs = Task.objects.bulk_create(
        [
            Task(**fields.dict())
            for fields in payload
        ]
    )
    return new_objs


@api.put("tasks/{task_id}/", response=TaskOut)
def update_tasks(request, task_id: int, payload: TaskIn):
    update_obj = get_object_or_404(Task, pk=task_id)

    for key, value in payload.dict().items():
        setattr(update_obj, key, value)

    update_obj.save()

    return update_obj


@api.delete("tasks/{task_id}/")
def delete_task(request, task_id: int):
    requested_object = get_object_or_404(Task, pk=task_id)
    requested_object.delete()

    return {'successfully deleted': 200}


@api.post("tasks/{task_id}/cws/")
def create_cws_for_task(request, task_id: int, payload: ComplianceIn):
    task = Task.objects.get(pk=task_id)
    cw_attrs = payload.dict()
    cw_attrs.update(task=task)
    cw = CW.objects.create(
        task=cw_attrs['task'],
        perform_date=cw_attrs['perform_date']
        )
    cw.save()


@api.get("tasks/{task_id}/cws/", response=list[ComplianceOut])
def get_cws_for_task(request, task_id: int):
    cws = CW.objects.filter(task=task_id)
    return cws


@api.delete("tasks/{task_id}/cws/{cw_id}/")
def delete_cw(request, cw_id):
    cw = BaseModel.get_object_or_404(CW, pk=cw_id)
    cw.delete()


@api.put("tasks/{task_id}/cws/{cw_id}/", response=ComplianceOut)
def update_cw(request, cw_id, payload: ComplianceIn):

    cw = BaseModel.get_object_or_404(CW, pk=cw_id)

    cw.perform_date = payload.dict()['perform_date']

    cw.save()

    return cw


urlpatterns = [
    path("", api.urls),
]
