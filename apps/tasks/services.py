from datetime import date

from dateutil.relativedelta import relativedelta
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import QuerySet

from .models import Task, CW, BaseModel


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


def cnt_next_due(perf_date, months):
    res_date = perf_date + relativedelta(months=months)
    return res_date


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
    old_due_month = update_obj.due_months

    for key, value in payload.items():
        setattr(update_obj, key, value)

    update_obj.save()

    if update_obj.due_months != old_due_month and update_obj.compliance:
        cw = update_obj.compliance
        cw.next_due_date = cnt_next_due(cw.perform_date, update_obj.due_months)
        cw.save()

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

    if task.due_months:
        next_due = cnt_next_due(payload['perform_date'], task.due_months)
        payload.update(next_due_date=next_due)

    cw = CW.objects.create(**payload)
    cw.save()

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


def update_cw(cw_pk: int, payload: dict) -> None:
    cw = BaseModel.get_object_or_404(CW, pk=cw_pk)

    validate_cw_perf_date(cw.task, payload['perform_date'])

    cw.perform_date = payload['perform_date']

    if cw.task.due_months:
        cw.next_due_date = cnt_next_due(cw.perform_date, cw.task.due_months)

    cw.save()

    return cw
