from django.db import models
from django.db.models import QuerySet
from django.utils import timezone
from django.shortcuts import get_object_or_404


class TolType(models.TextChoices):
    MONTHS = 'M'
    DAYS = 'D'
    PERCENTS = 'P'

    @classmethod
    def group_choices(cls, group_name):
        interval = {
            "DUE_UNIT": {
                cls.MONTHS: "Months",
                cls.DAYS: "Days",
            },
            "MOS_UNIT": {
                cls.MONTHS: "Months",
                cls.DAYS: "Days",
                cls.PERCENTS: "Percents"
            }
        }

        return [
            (choice, name)
            for choice, name in interval[group_name].items()
        ]


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
            return self.compliances.active().latest("perform_date")
        except CW.DoesNotExist:
            return None

    @property
    def curr_requirements(self) -> object | None:
        try:
            return self.requirements.active().filter(is_active=True).first()
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
    next_due_date = models.DateField("Next due date", blank=True, null=True)
    adj_mos = models.IntegerField("Adjustment", blank=True, null=True)

    class Meta:
        unique_together = ("task", "perform_date")

    def __str__(self):
        return f"CW for task: {self.task}"


class Requirements(BaseModel):

    task = models.ForeignKey(
        "Task",
        on_delete=models.CASCADE,
        related_name="requirements"
    )

    due_months = models.DecimalField(
        "Due_months",
        max_digits=4,
        decimal_places=2,
        blank=True,
        null=True
    )
    due_months_unit = models.CharField(
        max_length=1,
        choices=TolType.group_choices("DUE_UNIT")
    )

    tol_pos_mos = models.DecimalField(
        "MOS positive",
        max_digits=4,
        decimal_places=2,
        blank=True,
        null=True
    )
    tol_neg_mos = models.DecimalField(
        "MOS negative",
        max_digits=4,
        decimal_places=2,
        blank=True,
        null=True
    )
    tol_mos_unit = models.CharField(
        "MOS unit",
        choices=TolType.group_choices("MOS_UNIT"),
        max_length=1,
        blank=True,
        null=True
    )

    is_active = models.BooleanField("active_tolerance")

    def __str__(self):
        return f"{self.task} tolerance"
