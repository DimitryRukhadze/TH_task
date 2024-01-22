from math import ceil, floor
from datetime import date

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from dateutil.relativedelta import relativedelta

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
    return Task.objects.active().filter(pk=task_pk).exists()


def check_adjustment(task: Task, perform_date) -> bool:
    latest_cw = task.compliance

    if latest_cw and latest_cw.next_due_date:
        return latest_cw.next_due_date != perform_date
    return False


def count_adjustment(task: Task, perf_date):
    delta = perf_date - task.compliance.next_due_date
    return delta.days


def cnt_mos_span_days(tol: Requirements, late_cw: CW) -> tuple:
    if tol.pos_tol_mos:
        pos_tol_days = relativedelta(days=tol.pos_tol_mos)
        pos_span = late_cw.next_due_date + pos_tol_days
    else:
        pos_span = late_cw.next_due_date

    if tol.neg_tol_mos:
        neg_tol_days = relativedelta(days=tol.neg_tol_mos)
        neg_span = late_cw.next_due_date + neg_tol_days
    else:
        neg_span = late_cw.next_due_date

    return neg_span, pos_span


def cnt_mos_span_months(tol: Requirements, late_cw: CW) -> tuple:
    if tol.pos_tol_mos:
        add_months = int(tol.pos_tol_mos)

        if tol.pos_tol_mos % int(tol.pos_tol_mos):
            add_days = ceil(30.5 / (tol.pos_tol_mos % int(tol.pos_tol_mos)))
        else:
            add_days = 0

        pos_tol_months = relativedelta(days=ceil(add_days), months=add_months)
        pos_span = late_cw.next_due_date + pos_tol_months

    else:
        pos_span = late_cw.next_due_date

    if tol.neg_tol_mos:
        sub_months = int(tol.neg_tol_mos)

        if tol.neg_tol_mos % int(tol.neg_tol_mos):
            sub_days = ceil(30.5 / (tol.neg_tol_mos % int(tol.neg_tol_mos)))
        else:
            sub_days = 0
        neg_tol_months = relativedelta(days=sub_days, months=sub_months)
        neg_span = late_cw.next_due_date + neg_tol_months
    else:
        neg_span = late_cw.next_due_date

    return neg_span, pos_span


def cnt_mos_span_percents(
            tol: Requirements,
            late_cw: CW,
            due_months: int | float
        ) -> tuple:

    due_days = due_months * 30.5

    if tol.pos_tol_mos:
        pos_days = ceil(due_days * (tol.pos_tol_mos / 100))
        pos_span = late_cw.next_due_date + relativedelta(days=pos_days)
    else:
        pos_span = late_cw.next_due_date

    if tol.neg_tol_mos:
        neg_days = floor(due_days * (tol.neg_tol_mos / 100))
        neg_span = late_cw.next_due_date + relativedelta(days=neg_days)
    else:
        neg_span = late_cw.next_due_date

    return neg_span, pos_span


def get_mos_span(task: Task) -> date | None:
    tolerance = task.curr_requirements
    latest_cw = task.compliance

    if latest_cw:
        if tolerance.mos_unit == 'M':
            return cnt_mos_span_months(tolerance, latest_cw)
        if tolerance.mos_unit == 'D':
            return cnt_mos_span_days(tolerance, latest_cw)
        if tolerance.mos_unit == 'P':
            return cnt_mos_span_percents(tolerance, latest_cw, task.due_months)


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

    validate_cw_perf_date(task, payload['perform_date'])

    if check_adjustment(task, payload['perform_date']):
        tol_neg, tol_pos = get_mos_span(task)
        if not tol_neg and tol_pos:
            tol_neg = payload['perform_date']
        if not tol_pos and tol_neg:
            tol_pos = payload['perform_date']

        if tol_neg <= payload['perform_date'] <= tol_pos:
            adj = count_adjustment(task, payload['perform_date'])
            payload.update(adjusted_days=adj)

    payload.update(task=task)
    cw = CW.objects.create(**payload)
    cw.save()

    from .tasks import update_next_due_date
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

    from .tasks import update_next_due_date
    update_next_due_date.delay(cw.task.pk)

    return cw
