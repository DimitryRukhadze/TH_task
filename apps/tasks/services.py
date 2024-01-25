from datetime import date

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from ninja import Schema

from .models import Task, CW, BaseModel, Requirements
from .tasks import update_next_due_date


def validate_cw_perf_date(task: Task, perform_date: date) -> None:
    if perform_date > timezone.now().date():
        raise ValidationError(
            f"{perform_date} is in the future"
        )
    if task.compliance and task.compliance.perform_date >= perform_date:
        raise ValidationError(
            f"{perform_date} is before latest compliance"
        )


def validate_task_exists(task_pk: int) -> bool:
    if not Task.objects.active().filter(pk=task_pk).exists():
        raise ValidationError(
            f"Task with pk={task_pk} does not exist"
        )


def validate_dues(payload: Schema) -> bool:
    if not payload.due_months:
        raise ValidationError(
            "Can not create Requirements without dues"
        )
    if not payload.due_months_unit:
        raise ValidationError(
            "Can not create due months without unit"
        )


def validate_tol_units(payload: Schema):
    if payload.tol_pos_mos or payload.tol_neg_mos:
        if not payload.tol_mos_unit:
            raise ValidationError(
                'No unit for tolerances'
            )

    if payload.tol_mos_unit:
        if not payload.tol_pos_mos and not payload.tol_neg_mos:
            raise ValidationError(
                "Can not create Tolerance without values"
            )


def get_tasks() -> QuerySet:
    return Task.objects.active().order_by("code", "description")


def get_task(task_pk: int) -> Task | None:
    return get_object_or_404(Task, pk=task_pk)


def create_tasks(payload: list[dict]) -> list[Task]:
    new_objs = Task.objects.bulk_create(
        [
            Task(**fields)
            for fields in payload
        ]
    )
    return new_objs


def update_tasks(task_pk: int, payload: dict) -> Task:
    update_obj = get_object_or_404(Task, pk=task_pk)

    for key, value in payload.items():
        setattr(update_obj, key, value)

    update_obj.save()

    return update_obj


def delete_task(task_pk: int) -> dict:
    task = BaseModel.get_object_or_404(Task, pk=task_pk)
    if task:
        task_cws = CW.objects.filter(task=task)
    task.delete()
    task_cws.delete()


def create_cw(task_pk: int, payload: dict) -> CW:
    task = BaseModel.get_object_or_404(Task, pk=task_pk)

    validate_cw_perf_date(task, payload['perform_date'])

    payload.update(task=task)
    cw = CW.objects.create(**payload)
    cw.save()

    update_next_due_date.delay(task.pk)

    return cw


def get_cws(task_pk: int) -> QuerySet:
    task = BaseModel.get_object_or_404(Task, pk=task_pk)
    return CW.objects.filter(
            task=task.pk,
            is_deleted=False
        ).order_by("perform_date")


def delete_cw(cw_pk: int) -> None:
    cw = BaseModel.get_object_or_404(CW, pk=cw_pk)
    cw.delete()


def update_cw(cw_pk: int, payload: dict) -> CW:
    cw = BaseModel.get_object_or_404(CW, pk=cw_pk)

    validate_cw_perf_date(cw.task, payload['perform_date'])

    cw.perform_date = payload['perform_date']
    cw.save()

    update_next_due_date.delay(cw.task.pk)

    return cw


def create_req(task_pk: int, payload: Schema) -> Requirements:

    validate_task_exists(task_pk)
    validate_dues(payload)
    validate_tol_units(payload)
    task = BaseModel.get_object_or_404(Task, pk=task_pk)
    req = Requirements.objects.create(
        task=task,
        due_months=payload.due_months,
        due_months_unit=payload.due_months_unit,
        tol_pos_mos=payload.tol_pos_mos,
        tol_neg_mos=payload.tol_neg_mos,
        tol_mos_unit=payload.tol_mos_unit,
        is_active=payload.is_active
    )
    if task.curr_requirements and payload.is_active:
        curr_req = task.curr_requirements
        curr_req.is_active = False
        curr_req.save()

    req.save()
    if task.compliance:
        update_next_due_date.delay(task.pk)

    return req


def get_req(task_pk: int, req_pk: int):
    validate_task_exists(task_pk)
    return BaseModel.get_object_or_404(Requirements, pk=req_pk)


def update_req(task_pk: int, req_pk: int, payload: Schema) -> Requirements:
    validate_task_exists(task_pk)

    task = BaseModel.get_object_or_404(Task, pk=task_pk)
    req = BaseModel.get_object_or_404(Requirements, pk=req_pk)

    if not req.is_active and payload.is_active:
        curr_req = task.curr_requirements
        if curr_req:
            curr_req.is_active = False
            curr_req.save()

    update_attrs = payload.dict()

    for name, value in update_attrs.items():
        setattr(req, name, value)

    if req.due_months and not req.due_months_unit:
        req.due_months = None

    if (req.tol_pos_mos or req.tol_neg_mos) and not req.tol_mos_unit:
        req.tol_pos_mos = None
        req.tol_neg_mos = None

    req.save()

    return req


def delete_req(task_pk: int, req_pk: int):
    validate_task_exists(task_pk)
    req = BaseModel.get_object_or_404(Requirements, pk=req_pk)
    req.is_active = False
    req.delete()
    return req
