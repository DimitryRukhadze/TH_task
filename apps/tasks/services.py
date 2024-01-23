from datetime import date

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import QuerySet

from .models import Task, CW, BaseModel, Requirements
from .schemas import ReqIn
from .tasks import update_next_due_date
from .interval_maths import (
    check_adjustment,
    count_mos_adjustment,
    count_hrs_adjustment,
    count_afl_adjustment,
    get_mos_span,
    get_hrs_span,
    get_afl_span
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
    if not Task.objects.active().filter(pk=task_pk).exists():
        raise ValidationError(
            "No such Task"
        )


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
        tol_neg_hrs, tol_pos_hrs = get_hrs_span(task)
        if not tol_neg_hrs and tol_pos_hrs:
            tol_neg_mos = payload['perform_hours']
        if not tol_pos_hrs and tol_neg_hrs:
            tol_pos_mos = payload['perform_hours']

        req['hrs_pos'] = tol_pos_hrs
        req['hrs_neg'] = tol_neg_hrs

    if active_req.afl_unit != "Empty":
        tol_neg_afl, tol_pos_afl = get_afl_span(task)
        if not tol_neg_afl and tol_pos_afl:
            tol_neg_afl = payload['perform_cycles']
        if not tol_pos_afl and tol_neg_afl:
            tol_pos_afl = payload['perform_cycles']

        req['afl_pos'] = tol_pos_afl
        req['afl_neg'] = tol_neg_afl

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
        adj = {}
        if active_req.mos_unit != 'E' and (req['mos_neg'] <= payload['perform_date'] <= req['mos_pos']):
            adj["adjusted_days"] = count_mos_adjustment(task, payload)

        if active_req.hrs_unit != 'E' and (req['hrs_neg'] <= payload['perform_hours'] <= req['hrs_pos']):
            adj["adjusted_hrs"] = count_hrs_adjustment(task, payload)

        if active_req.afl_unit != 'E' and (req['afl_neg'] <= payload['perform_cycles'] <= req['afl_pos']):
            adj["adjusted_cycles"] = count_afl_adjustment(task, payload)

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


def create_requirements(task_id: int, payload: ReqIn) -> Requirements:

    validate_task_exists(task_id)
    task = Task.objects.get(pk=task_id)

    if payload.is_active:
        act_reqs = task.curr_requirements
        act_reqs.is_active = False
        act_reqs.save()

    req = Requirements.objects.create(
        task=task,
        mos_unit=payload.mos_unit,
        hrs_unit=payload.hrs_unit,
        afl_unit=payload.afl_unit,
        due_months=payload.due_months or 0,
        due_hrs=payload.due_hrs or 0,
        due_cycles=payload.due_cycles or 0,
        pos_tol_mos=payload.pos_tol_mos,
        neg_tol_mos=payload.neg_tol_mos,
        pos_tol_hrs=payload.pos_tol_hrs,
        neg_tol_hrs=payload.neg_tol_hrs,
        pos_tol_afl=payload.pos_tol_afl,
        neg_tol_afl=payload.neg_tol_afl,
        is_active=payload.is_active
    )

    req.save()
    return req


def get_task_reqs(task_id) -> list[Requirements]:
    validate_task_exists(task_id)
    reqs = Requirements.objects.active().filter(task__pk=task_id)
    return reqs


def update_requirements(task_id, req_id, payload):
    validate_task_exists(task_id)
    req = BaseModel.get_object_or_404(Requirements, pk=req_id)
    if payload.task:
        req.task = payload.task
    if payload.mos_unit:
        req.mos_unit = payload.mos_unit
    if payload.hrs_unit:
        req.hrs_unit = payload.hrs_unit
    if payload.afl_unit:
        req.afl_unit = payload.afl_unit
    if payload.due_months:
        req.due_months = payload.due_months
    if payload.due_hrs:
        req.due_hrs = payload.due_hrs
    if payload.due_cycles:
        req.due_cycles = payload.due_cycles
    if payload.pos_tol_mos:
        req.pos_tol_mos = payload.pos_tol_mos
    if payload.neg_tol_mos:
        req.neg_tol_mos = payload.neg_tol_mos
    if payload.pos_tol_hrs:
        req.pos_tol_hrs = payload.pos_tol_hrs
    if payload.neg_tol_hrs:
        req.neg_tol_hrs = payload.neg_tol_hrs
    if payload.pos_tol_afl:
        req.pos_tol_afl = payload.pos_tol_afl
    if payload.neg_tol_afl:
        req.neg_tol_afl = payload.neg_tol_afl
    if payload.is_active:
        req.is_active = payload.is_active

    req.save()
    return req

def delete_requirements():
    pass
