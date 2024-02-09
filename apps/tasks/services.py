from decimal import Decimal


from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import QuerySet, Prefetch
from django.forms.models import model_to_dict

from .schemas import ReqIn, ComplianceIn, TaskIn
from .models import Task, CW, Requirements, UnitType
from .tasks import update_next_due_date
from .interval_maths import get_prev_cw


def validate_cw_perf_hrs(payload: ComplianceIn, prev_cw: CW, req: Requirements) -> None:

    if req and req.due_hrs and payload.perform_hrs is None:
        raise ValidationError(
            "Can't create empty HRS cw with HRS due"
        )

    if payload.perform_hrs > 1000000:
        raise ValidationError(
            "Performance HRS too large"
        )
    if payload.perform_hrs < 0:
        raise ValidationError(
            "Can't create negative HRS"
        )

    if prev_cw and prev_cw.perform_hrs and prev_cw.perform_hrs > payload.perform_hrs:
        raise ValidationError(
            "Performance hours is before previous CW"
        )


def validate_cw_perf_cyc(payload: ComplianceIn, prev_cw: CW, req: Requirements) -> None:

    if req and req.due_cyc and payload.perform_cyc is None:
        raise ValidationError(
            "Can't create empty CYC cw with CYC dues"
        )

    if payload.perform_cyc > 1000000:
        raise ValidationError(
            "Performance CYC too large"
        )

    # Надо ли делать валидацию > 0, если в модели PositiveInteger ?

    if prev_cw and prev_cw.perform_cyc and prev_cw.perform_cyc > payload.perform_cyc:
        raise ValidationError(
            "Performance cycles is before previous CW"
        )


def validate_cw_perform_date(payload: ComplianceIn, prev_cw: CW | None) -> None:
    if payload.perform_date > timezone.now().date():
        raise ValidationError(
            f"{payload.perform_date} is in the future"
        )

    if payload.perform_date.year <= 1990:
        raise ValidationError(
            "Invaild CW year. Too old."
        )

    if prev_cw and prev_cw.perform_date >= payload.perform_date:
        raise ValidationError(
            "Performance date is before or equal previous CW"
        )


def validate_cw_is_latest(cw: CW):
    if cw != cw.task.compliance:
        raise ValidationError(
            "Can't change previous compliances"
        )


def validate_dues(payload: ReqIn) -> None:
    if not payload.due_months and not payload.due_hrs and not payload.due_cyc:
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

    if payload.due_months is not None:
        if payload.due_months > 27375:  # 27375 days = 75 years
            raise ValidationError(
                "Due months exceeds max aircraft lifespan"
            )
        if payload.due_months < 1:
            raise ValidationError(
                "MOS must be greater then 0"
            )

    if payload.due_hrs is not None:
        if payload.due_hrs > 1000000:
            raise ValidationError(
                "HRS number too large"
            )

        if payload.due_hrs < 0.01:
            raise ValidationError(
                "HRS due must be greater than 0"
            )

    if payload.due_cyc is not None:
        if payload.due_cyc > 1000000:
            raise ValidationError(
                "CYC number too large"
            )
        if payload.due_cyc < 1:
            raise ValidationError(
                "CYC must be greater then 0"
            )


def validate_tol_value(tol: Decimal):
    if tol < 0:
        raise ValidationError(
            "Tolerance must be a positive number"
        )


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

    no_due = ValidationError(
        "No due for tolerance"
    )

    if (payload.tol_pos_mos or payload.tol_neg_mos) and not payload.tol_mos_unit:
        raise no_units

    if (payload.tol_pos_hrs or payload.tol_neg_hrs) and not payload.tol_hrs_unit:
        raise no_units

    if (payload.tol_pos_cyc or payload.tol_neg_cyc) and not payload.tol_cyc_unit:
        raise no_units

    if payload.tol_mos_unit and (not payload.tol_pos_mos and not payload.tol_neg_mos):
        raise no_values

    if payload.tol_hrs_unit and (not payload.tol_pos_hrs and not payload.tol_neg_hrs):
        raise no_values

    if payload.tol_cyc_unit and (not payload.tol_pos_cyc and not payload.tol_neg_cyc):
        raise no_values

    if payload.tol_mos_unit and payload.tol_mos_unit not in UnitType.provide_choice_types("MOS_UNIT"):
        raise wrong_tol_type

    if payload.tol_hrs_unit and payload.tol_hrs_unit not in UnitType.provide_choice_types("HRS_UNIT"):
        raise wrong_tol_type

    if payload.tol_cyc_unit and payload.tol_cyc_unit not in UnitType.provide_choice_types("CYC_UNIT"):
        raise wrong_tol_type

    if not payload.due_months and (payload.tol_pos_mos or payload.tol_neg_mos):
        raise no_due

    if not payload.due_hrs and (payload.tol_pos_hrs or payload.tol_neg_hrs):
        raise no_due

    if not payload.due_cyc and (payload.tol_pos_cyc or payload.tol_neg_cyc):
        raise no_due

    if payload.tol_pos_mos:
        validate_tol_value(payload.tol_pos_mos)
    if payload.tol_neg_mos:
        validate_tol_value(payload.tol_neg_mos)
    if payload.tol_pos_hrs:
        validate_tol_value(payload.tol_pos_hrs)
    if payload.tol_neg_hrs:
        validate_tol_value(payload.tol_neg_hrs)
    if payload.tol_pos_cyc:
        validate_tol_value(payload.tol_pos_cyc)
    if payload.tol_neg_cyc:
        validate_tol_value(payload.tol_neg_cyc)


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
    curr_req = task.curr_requirements
    validate_cw_perform_date(payload, prev_cw)

    if payload.perform_hrs or (curr_req and curr_req.due_hrs):
        validate_cw_perf_hrs(payload, prev_cw, curr_req)
    if payload.perform_cyc or (curr_req and curr_req.due_cyc):
        validate_cw_perf_cyc(payload, prev_cw, curr_req)

    CW.objects.create(
        task=task,
        perform_date=payload.perform_date,
        perform_hrs=payload.perform_hrs,
        perform_cyc=payload.perform_cyc
    )

    update_next_due_date.delay(task.pk)


def get_cws(task: Task) -> QuerySet:
    return CW.objects.active().filter(task=task).order_by("perform_date")


def update_cw(task: Task, cw: CW, payload: ComplianceIn) -> None:
    curr_req = task.curr_requirements
    prev_cw = get_prev_cw(task)

    validate_cw_is_latest(cw)
    validate_cw_perform_date(payload, prev_cw)

    if payload.perform_hrs:
        validate_cw_perf_hrs(payload, prev_cw, curr_req)
    if payload.perform_cyc:
        validate_cw_perf_cyc(payload, prev_cw, curr_req)

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
        due_hrs=payload.due_hrs,
        due_cyc=payload.due_cyc,
        tol_pos_mos=payload.tol_pos_mos,
        tol_neg_mos=payload.tol_neg_mos,
        tol_mos_unit=payload.tol_mos_unit,
        tol_pos_hrs=payload.tol_pos_hrs,
        tol_neg_hrs=payload.tol_neg_hrs,
        tol_hrs_unit=payload.tol_hrs_unit,
        tol_pos_cyc=payload.tol_pos_cyc,
        tol_neg_cyc=payload.tol_neg_cyc,
        tol_cyc_unit=payload.tol_cyc_unit,
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

    validate_dues(payload)
    validate_tol_units(payload)

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
