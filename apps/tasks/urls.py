from django.urls import path


from ninja.router import Router

from .models import Task, CW, BaseModel
from .schemas import TaskIn, TaskOut, ComplianceIn, ComplianceOut
from .services import (
    get_tasks,
    get_task,
    create_tasks,
    update_tasks,
    delete_task,
    create_cw,
    get_cws,
    delete_cw,
    update_cw
    )


router = Router()


@router.get("", response=list[TaskOut])
def api_get_tasks(request):
    return get_tasks()


@router.get("{task_id}/", response=TaskOut)
def api_get_task(request, task_id: int):
    return get_task(task_id)


@router.post("", response=list[TaskOut])
def api_create_tasks(request, payload: list[TaskIn]):
    payload = [fields.dict() for fields in payload]
    return create_tasks(payload)


@router.put("{task_id}/", response=TaskOut)
def api_update_tasks(request, task_id: int, payload: TaskIn):
    return update_tasks(task_id, payload.dict())


@router.delete("{task_id}/")
def api_delete_task(request, task_id: int):
    return delete_task(task_id)


@router.post("{task_id}/cws/", response=ComplianceOut)
def api_create_cws(request, task_id: int, payload: ComplianceIn):
    return create_cw(task_id, payload.dict())


@router.get("{task_id}/cws/", response=list[ComplianceOut])
def api_get_cws(request, task_id: int):
    return get_cws(task_id)


@router.delete("{task_id}/cws/{cw_id}/")
def api_delete_cw(request, cw_id):
    return delete_cw(cw_id)


@router.put("{task_id}/cws/{cw_id}/", response=ComplianceOut)
def api_update_cw(request, cw_id, payload: ComplianceIn):
    return update_cw(cw_id, payload.dict())
