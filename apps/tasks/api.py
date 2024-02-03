from ninja.router import Router
from ninja.pagination import paginate, LimitOffsetPagination

from django.core.exceptions import ValidationError
from django.db.models import Prefetch
from .models import BaseModel, Task, CW, Requirements

from .schemas import (
    TaskIn,
    TaskOut,
    ListTaskOut,
    ComplianceIn,
    ComplianceOut,
    ReqIn,
    ReqOut,
    Error
    )
from .services import (
    get_tasks,
    create_tasks,
    update_task,
    delete_task,
    create_cw,
    get_cws,
    delete_cw,
    update_cw,
    create_req,
    update_req,
    delete_req
    )


router = Router()


@router.get("", response=list[ListTaskOut])
@paginate(LimitOffsetPagination)
def api_get_tasks(request):
    return get_tasks()


@router.get("{task_id}/", response=TaskOut)
def api_get_task(request, task_id: int):
    return BaseModel.get_object_or_404(Task, pk=task_id)


@router.post("", response=list[TaskOut])
@paginate
def api_create_tasks(request, payload: list[TaskIn]):
    payload = [fields.dict() for fields in payload]
    return create_tasks(payload)


@router.put("{task_id}/", response=TaskOut)
def api_update_task(request, task_id: int, payload: TaskIn):
    task = BaseModel.get_object_or_404(Task, pk=task_id)
    return update_task(task, payload.dict())


@router.delete("{task_id}/")
def api_delete_task(request, task_id: int):
    task = BaseModel.get_object_or_404(Task, pk=task_id)
    return delete_task(task)


@router.post(
        "{task_id}/cws/",
        response={
            201: None,
            400: Error
            }
        )
def api_create_cw(request, task_id: int, payload: ComplianceIn):
    task = BaseModel.get_object_or_404(Task, pk=task_id)
    try:
        create_cw(task, payload)
    except ValidationError as err:
        return 400, {"message": err.message}
    return 201, None


@router.get("{task_id}/cws/", response=list[ComplianceOut])
@paginate
def api_get_cws(request, task_id: int):
    task = BaseModel.get_object_or_404(Task, pk=task_id)
    return get_cws(task)


@router.delete("{task_id}/cws/{cw_id}/")
def api_delete_cw(request, cw_id, task_id):
    task = BaseModel.get_object_or_404(Task, pk=task_id)
    cw = BaseModel.get_object_or_404(CW, pk=cw_id, task=task)
    return delete_cw(cw)


@router.put(
        "{task_id}/cws/{cw_id}/",
        response={
            200: None,
            400: Error
            }
        )
def api_update_cw(request, task_id, cw_id, payload: ComplianceIn):
    task = BaseModel.get_object_or_404(Task, pk=task_id)
    cw = BaseModel.get_object_or_404(CW, pk=cw_id, task=task)
    try:
        update_cw(cw, payload)
    except ValidationError as err:
        return 400, {"message": err.message}
    return 200, None


@router.post(
        "{task_id}/requirements/",
        response={
            200: ReqOut,
            400: Error
        }
    )
def api_create_req(request, task_id, payload: ReqIn):
    task = BaseModel.get_object_or_404(Task, pk=task_id)
    try:
        new_req = create_req(task, payload)
    except ValidationError as err:
        return 400, {"message": err.message}
    return 200, new_req


@router.get(
        "{task_id}/requirements/{req_id}/",
        response={200: ReqOut, 400: Error}
    )
def api_get_req(request, task_id: int, req_id: int):
    return BaseModel.get_object_or_404(Requirements, pk=req_id, task__pk=task_id)


@router.put(
        "{task_id}/requirements/{req_id}/",
        response={200: ReqOut, 400: Error}
    )
def api_update_req(request, task_id, req_id, payload: ReqIn):
    requirement = BaseModel.get_object_or_404(Requirements, pk=req_id, task__pk=task_id)
    try:
        req = update_req(requirement, payload)
    except ValidationError as err:
        return 400, {"message": err.message}
    return 200, req


@router.delete(
        "{task_id}/requirements/{req_id}/",
        response={200: None, 400: Error}
    )
def api_delete_req(request, task_id, req_id):
    req = BaseModel.get_object_or_404(Requirements, pk=req_id, task__pk=task_id)
    try:
        delete_req(req)
    except ValidationError as err:
        return 400, {"message": err.message}
    return 200, None
