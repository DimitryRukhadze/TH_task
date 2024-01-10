from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models import Task, CW, BaseModel


def validate_cw_perf_date(task: Task, perform_date):
    if perform_date > timezone.now().date():
        raise ValidationError(
            f"{perform_date} is in the future"
        )
    if task.compliance and task.compliance.perform_date >= perform_date:
        raise ValidationError(
            f"{perform_date} is before latest compliance"
        )


def get_tasks():
    return Task.objects.active().order_by("code", "description")


def get_task(task_pk):
    return get_object_or_404(Task, pk=task_pk)


def create_tasks(payload):
    new_objs = Task.objects.bulk_create(
        [
            Task(**fields)
            for fields in payload
        ]
    )
    return new_objs


def update_tasks(task_pk, payload):
    update_obj = get_object_or_404(Task, pk=task_pk)

    for key, value in payload.items():
        setattr(update_obj, key, value)

    update_obj.save()

    return update_obj


def delete_task(task_pk):
    requested_object = get_object_or_404(Task, pk=task_pk)
    requested_object.delete()

    return {200: 'Succesfully deleted'}


def create_cw(task_pk, payload):
    task = Task.objects.get(pk=task_pk)

    try:
        validate_cw_perf_date(task, payload['perform_date'])
    except ValidationError:
        raise

    payload.update(task=task)
    cw = CW.objects.create(**payload)
    cw.save()
    return cw


def get_cws(task_pk):
    return CW.objects.filter(task=task_pk, is_deleted=False)


def delete_cw(cw_pk):
    cw = BaseModel.get_object_or_404(CW, pk=cw_pk)
    cw.delete()
    # Что вернуть??
    return


def update_cw(cw_pk, payload):
    cw = BaseModel.get_object_or_404(CW, pk=cw_pk)
    try:
        validate_cw_perf_date(cw.task, payload['perform_date'])
    except ValidationError:
        raise

    cw.perform_date = payload['perform_date']
    cw.save()

    return cw
