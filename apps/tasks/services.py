from datetime import date

from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import QuerySet, Prefetch
from django.forms.models import model_to_dict

from .schemas import ReqIn, ComplianceIn, TaskIn
from .models import Task, CW, Requirements, UnitType
from .tasks import update_next_due_date
from .interval_maths import get_prev_cw


def validate_cw_perf_date(perform_date: date, prev_cw: CW | None) -> None:
    if perform_date > timezone.now().date():
        raise ValidationError(
            f"{perform_date} is in the future"
        )

    if prev_cw and prev_cw.perform_date >= perform_date:
        raise ValidationError(
            "Perfrom date is before or equal previous CW"
        )

    if perform_date.year <= 1990:
        raise ValidationError(
            "Invaild CW year. Too old."
        )


def validate_cw_is_latest(cw: CW):
    if cw != cw.task.compliance:
        raise ValidationError(
            "Can't change previous compliances"
        )


def validate_due_mos_extremes(payload: ReqIn) -> None:
    if payload.due_months < 0:
        raise ValidationError(
            "due_months should be a valid positive integer"
        )

    if payload.due_months > 27375:  # 27375 days = 75 years
        raise ValidationError(
            "Due months exceeds max aircraft lifespan"
        )


def validate_dues(payload: ReqIn) -> None:
    if not payload.due_months and not payload.due_hrs:
        raise ValidationError(
            "Can not create Requirements without dues"
        )
    if payload.due_months and not payload.due_months_unit:
        raise ValidationError(
            "Can not create due months without unit"
        )

    if payload.due_months_unit and payload.due_months_unit not in UnitType.provide_choice_types("DUE_UNIT"):
        raise ValidationError(
            f"No {payload.due_months_unit} due months type"
        )
    validate_due_mos_extremes(payload)


def validate_tol_units(payload: ReqIn):
    no_units = ValidationError(
            'No unit for tolerances'
        )
    no_values = ValidationError(
            "Can not create Tolerance without values"
        )
    wrong_tol_type = ValidationError(
            f"No {payload.tol_mos_unit} tolerance type"
        )
    if (payload.tol_pos_mos or payload.tol_neg_mos) and not payload.tol_mos_unit:
        raise no_units

    if (payload.tol_pos_hrs or payload.tol_neg_hrs) and not payload.tol_hrs_unit:
        raise no_units

    if payload.tol_mos_unit and (not payload.tol_pos_mos and not payload.tol_neg_mos):
        raise no_values

    if payload.tol_hrs_unit and (not payload.tol_pos_hrs and not payload.tol_neg_hrs):
        raise no_values

    if payload.tol_mos_unit and payload.tol_mos_unit not in UnitType.provide_choice_types("MOS_UNIT"):
        raise wrong_tol_type

    if payload.tol_hrs_unit and payload.tol_hrs_unit not in UnitType.provide_choice_types("HRS_UNIT"):
        raise wrong_tol_type


def get_tasks() -> QuerySet:
    compliance_qs = CW.objects.active().order_by("-perform_date")[:1]
    requirement_qs = Requirements.objects.active().filter(is_active=True)[:1]
    pre_cw = Prefetch("compliances", queryset=compliance_qs, to_attr="compliance_qs")
    pre_req = Prefetch("requirements", queryset=requirement_qs, to_attr='requirement_qs')

    return Task.objects.active().prefetch_related(pre_cw).prefetch_related(pre_req).order_by("code", "description")


def create_tasks(payload: list[dict]) -> list[Task]:
    return Task.objects.bulk_create([Task(**fields) for fields in payload])


def update_task(task: Task, payload: TaskIn) -> Task:

    for key, value in payload.dict(exclude_unset=True).items():
        setattr(task, key, value)

    task.save()

    return task


def delete_task(task: Task):
    cws = CW.objects.active().filter(task=task)
    requirements = Requirements.objects.active().filter(task=task)
    for cw in cws:
        cw.delete()
    for req in requirements:
        req.delete()

    task.delete()


def create_cw(task: Task, payload: ComplianceIn) -> None:
    prev_cw = task.compliance
    validate_cw_perf_date(payload.perform_date, prev_cw)

    CW.objects.create(task=task, perform_date=payload.perform_date)

    update_next_due_date.delay(task.pk)


def get_cws(task: Task) -> QuerySet:
    return CW.objects.active().filter(task=task).order_by("perform_date")


def update_cw(task: Task, cw: CW, payload: ComplianceIn) -> None:

    validate_cw_is_latest(cw)
    validate_cw_perf_date(payload.perform_date, prev_cw=get_prev_cw(task))

    cw.perform_date = payload.perform_date
    cw.save()

    update_next_due_date.delay(cw.task.pk)


def delete_cw(cw: CW) -> None:
    cw.delete()
    update_next_due_date.delay(cw.task.pk)


def create_req(task: Task, payload: ReqIn) -> Requirements:

    validate_dues(payload)
    validate_tol_units(payload)

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


def update_req(req: Requirements, payload: ReqIn) -> Requirements:

    if payload.due_months:
        validate_due_mos_extremes(payload)

    if req.is_active is False and payload.is_active:
        if curr_req := req.task.curr_requirements:
            curr_req.is_active = False
            curr_req.save()
    update_attrs = payload.dict(exclude_unset=True)

    req_fields = model_to_dict(req)

    for name, value in update_attrs.items():
        if req_fields.get(name) != value:
            setattr(req, name, value)

    if req.due_months and not req.due_months_unit:
        req.due_months = None

    if (req.tol_pos_mos or req.tol_neg_mos) and not req.tol_mos_unit:
        req.tol_pos_mos = None
        req.tol_neg_mos = None

    if not req.tol_pos_mos and not req.tol_neg_mos:
        req.tol_mos_unit = None

    req.save()
    update_next_due_date.delay(req.task.pk)

    return req


def delete_req(req: Requirements) -> None:
    req.delete()
    update_next_due_date.delay(req.task.pk)
