from ninja.router import Router
from ninja.pagination import paginate

from django.core.exceptions import ValidationError

from .schemas import (
    TaskIn,
    TaskOut,
    ComplianceIn,
    ComplianceOut,
    ReqIn,
    ReqOut,
    Error
)
from .services import (
    get_tasks,
    get_task,
    create_tasks,
    update_tasks,
    delete_task,
    create_cw,
    get_cws,
    delete_cw,
    update_cw,
    get_task_reqs,
    create_requirements,
    update_requirements,
    delete_requirements
)


router = Router()


@router.get("", response=list[TaskOut])
@paginate
def api_get_tasks(request):
    return get_tasks()


@router.get("{task_id}/", response=TaskOut)
def api_get_task(request, task_id: int):
    return get_task(task_id)


@router.post("", response=list[TaskOut])
@paginate
def api_create_tasks(request, payload: list[TaskIn]):
    payload = [fields.dict() for fields in payload]
    return create_tasks(payload)


@router.put("{task_id}/", response=TaskOut)
def api_update_tasks(request, task_id: int, payload: TaskIn):
    return update_tasks(task_id, payload.dict())


@router.delete("{task_id}/")
def api_delete_task(request, task_id: int):
    return delete_task(task_id)


@router.post(
        "{task_id}/cws/",
        response={
            200: ComplianceOut,
            400: Error
            }
        )
def api_create_cws(request, task_id: int, payload: ComplianceIn):
    try:
        new_cw = create_cw(task_id, payload.dict())
    except ValidationError as err:
        return 400, {"message": err.message}
    return new_cw


@router.get("{task_id}/cws/", response=list[ComplianceOut])
@paginate
def api_get_cws(request, task_id: int):
    return get_cws(task_id)


@router.delete("{task_id}/cws/{cw_id}/")
def api_delete_cw(request, cw_id):
    return delete_cw(cw_id)


@router.put(
        "{task_id}/cws/{cw_id}/",
        response={
            200: ComplianceOut,
            400: Error
            }
        )
def api_update_cw(request, cw_id, payload: ComplianceIn):
    try:
        cw = update_cw(cw_id, payload.dict())
    except ValidationError as err:
        return 400, {"message": err.message}
    return cw


@router.get("{task_id}/requirements/", response=list[ReqOut])
def api_get_requirements(request, task_id: int):
    return get_task_reqs(task_id)


@router.post("{task_id}/requirements/", response={200: ReqOut, 400: Error})
def api_create_requirements(request, task_id, payload: ReqIn):
    try:
        req = create_requirements(task_id, payload)
    except ValidationError as err:
        return 400, {"message": err.message}
    return req


@router.put(
        "{task_id}/requirements/{req_id}/",
        response={200: ReqOut, 400: Error}
    )
def api_update_requirements(request, task_id, req_id, payload: ReqIn):
    try:
        req = update_requirements(task_id, req_id, payload)
    except ValidationError as err:
        return 400, {"message": err.message}
    return req


@router.delete("{task_id}/requirements/{req_id}/")
def api_delete_requirements(request, req_id):
    return delete_requirements(req_id)
