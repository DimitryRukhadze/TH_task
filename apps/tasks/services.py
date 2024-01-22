from datetime import date

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import QuerySet

from .models import Task, CW, BaseModel
from .tasks import update_next_due_date
from .interval_maths import (
    check_adjustment,
    count_adjustment,
    get_mos_span,
    get_hrs_span
)


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
    return Task.objects.active().filter(pk=task_pk).exists()


def get_task_requirements(task_pk: int, payload: dict) -> dict:
    task = BaseModel.get_object_or_404(Task, pk=task_pk)
    active_req = task.curr_requirements

    req = {}

    if active_req.mos_unit != "E":
        tol_neg_mos, tol_pos_mos = get_mos_span(task)
        if not tol_neg_mos and tol_pos_mos:
            tol_neg_mos = payload['perform_date']
        if not tol_pos_mos and tol_neg_mos:
            tol_pos_mos = payload['perform_date']

        req['mos_pos'] = tol_pos_mos
        req['mos_neg'] = tol_neg_mos

    if active_req.hrs_unit != "E":
        tol_neg_mos, tol_pos_mos = get_hrs_span(task)
        if not tol_neg_mos and tol_pos_mos:
            tol_neg_mos = payload['perform_date']
        if not tol_pos_mos and tol_neg_mos:
            tol_pos_mos = payload['perform_date']

        req['hrs_pos'] = tol_pos_mos
        req['hrs_neg'] = tol_neg_mos

#    if active_req.afl_unit != "Empty":
#        tol_neg_mos, tol_pos_mos = get_afl_span(task)
#        if not tol_neg_mos and tol_pos_mos:
#            tol_neg_mos = payload['perform_date']
#        if not tol_pos_mos and tol_neg_mos:
#            tol_pos_mos = payload['perform_date']
#
#        req['afl_pos'] = tol_pos_mos
#        req['afl_neg'] = tol_neg_mos

        return req


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

    update_next_due_date.delay(task_pk)

    return update_obj


def delete_task(task_pk: int) -> dict:
    task = BaseModel.get_object_or_404(Task, pk=task_pk)
    if task:
        task_cws = CW.objects.filter(task=task)
    task.delete()
    task_cws.delete()


def create_cw(task_pk: int, payload: dict) -> CW:
    task = BaseModel.get_object_or_404(Task, pk=task_pk)
    active_req = task.curr_requirements

    validate_cw_perf_date(task, payload['perform_date'])

    if check_adjustment(task, payload):
        req = get_task_requirements(task_pk, payload)

        if active_req.mos_unit != 'E' and (req['mos_neg'] <= payload['perform_date'] <= req['mos_pos']):
            adj = count_adjustment(task, payload)

        if active_req.hrs_unit != 'E' and (req['hrs_neg'] <= payload['perform_hours'] <= req['hrs_pos']):
            adj = count_adjustment(task, payload)

        payload.update(adj)

    payload.update(task=task)
    cw = CW.objects.create(**payload)
    cw.save()

    update_next_due_date.delay(task_pk)

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
