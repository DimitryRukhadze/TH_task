from django.db import models
from django.db.models import QuerySet, UniqueConstraint, Q
from django.utils import timezone
from django.shortcuts import get_object_or_404


class BaseQuerySet(QuerySet):
    def active(self: QuerySet) -> QuerySet:
        return self.filter(is_deleted=False)


class BaseModel(models.Model):
    is_deleted = models.BooleanField("Deleted", default=False)

    created_at = models.DateTimeField(
        "Created",
        db_index=True,
        default=timezone.now
        )
    updated_at = models.DateTimeField("Changed", auto_now=True)

    objects = BaseQuerySet.as_manager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs) -> None:
        if self._state.adding and hasattr(self, "is_deleted"):
            self.is_deleted = False

        return super().save(*args, **kwargs)

    def delete(self):
        if hasattr(self, "is_deleted"):
            self.is_deleted = True
            self.save()

    @staticmethod
    def get_object_or_404(obj: object, **kwargs) -> object:
        return get_object_or_404(obj, is_deleted=False, **kwargs)


class Task(BaseModel):
    code = models.CharField("Task code", max_length=250)
    description = models.TextField("Description")

    def __str__(self):
        return self.code

    @property
    def compliance(self) -> object | None:
        try:
            return self.compliances.latest("perform_date")
        except CW.DoesNotExist:
            return None

    @property
    def curr_requirements(self) -> object | None:
        try:
            return self.requirements.latest("is_active")
        except Requirements.DoesNotExist:
            return None


class CW(BaseModel):
    task = models.ForeignKey(
            "Task",
            on_delete=models.CASCADE,
            related_name="compliances"
        )
    perform_date = models.DateField(
            "Perform date",
        )
    perform_hours = models.FloatField(
            "Perform hours",
            default=0,
            blank=True,
            null=True
        )
    perform_cycles = models.FloatField(
            "Perform cycles",
            default=0,
            blank=True,
            null=True
        )
    next_due_date = models.DateField("Next due date", blank=True, null=True)
    next_due_hrs = models.FloatField("Next due hours", blank=True, null=True)
    next_due_cycles = models.FloatField(
            "Next due cycles",
            blank=True,
            null=True
        )
    adjusted_days = models.IntegerField("Adjustment mos", default=0)
    adjusted_hrs = models.FloatField("Adjustment hrs", default=0)
    adjusted_cycles = models.FloatField("Adjustment cycles", default=0)

    class Meta:
        unique_together = ("task", "perform_date")

    def __str__(self):
        return f"CW for task: {self.task}"


class Requirements(BaseModel):
    class TolType(models.TextChoices):
        MONTHS = "M"
        DAYS = "D"
        PERCENTS = "P"
        HOURS = "H"
        CYCLES = "C"
        EMPTY = "E"

        @classmethod
        def group_choices(cls, group_name: str) -> list:
            intervals = {
                "MOS": {
                    cls.MONTHS: "Months",
                    cls.DAYS: "Days",
                    cls.PERCENTS: "Percents",
                    cls.EMPTY: "Empty"
                },
                "HRS": {
                    cls.HOURS: "Hours",
                    cls.PERCENTS: "Percents",
                    cls.EMPTY: "Empty"
                },
                "AFL/ENC": {
                    cls.CYCLES: "Cycles",
                    cls.PERCENTS: "Percents",
                    cls.EMPTY: "Empty"
                }
            }

            return [
                (name, value)
                for name, value in intervals[group_name].items()
            ]

    task = models.ForeignKey(
        "Task",
        on_delete=models.CASCADE,
        related_name="requirements"
    )
    due_months = models.IntegerField("Due months", blank=True, null=True)
    due_hrs = models.FloatField("Due hours", blank=True, null=True)
    due_cycles = models.FloatField("Due cycles", blank=True, null=True)

    pos_tol_mos = models.FloatField("MOS positive", blank=True, null=True)
    neg_tol_mos = models.FloatField("MOS negative", blank=True, null=True)
    mos_unit = models.CharField(
            "MOS unit",
            choices=TolType.group_choices('MOS'),
            max_length=1,
            default=TolType.EMPTY
        )

    pos_tol_hrs = models.FloatField("HRS positive", blank=True, null=True)
    neg_tol_hrs = models.FloatField("HRS negative", blank=True, null=True)
    hrs_unit = models.CharField(
            "HRS unit",
            choices=TolType.group_choices("HRS"),
            max_length=1,
            default=TolType.EMPTY
        )

    pos_tol_afl = models.FloatField("AFL/ENC positive", blank=True, null=True)
    neg_tol_afl = models.FloatField("AFL/ENC negative", blank=True, null=True)
    afl_unit = models.CharField(
            "AFL/ENC unit",
            choices=TolType.group_choices("AFL/ENC"),
            max_length=1,
            default=TolType.EMPTY
        )

    is_active = models.BooleanField("active_tolerance", default=False)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["task", "is_active"],
                condition=Q(is_active=True),
                name="unique_active_tolerance_for_task"
            )
        ]

    def __str__(self):
        return f"{self.task} requirements"
