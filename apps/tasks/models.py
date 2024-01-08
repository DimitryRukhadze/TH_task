from django.db import models
from django.db.models import QuerySet, Q
from django.utils import timezone
from django.shortcuts import get_object_or_404


class BaseQuerySet(QuerySet):
    def active(self: QuerySet) -> QuerySet:
        return self.filter(is_deleted=False)


class BaseModel(models.Model):
    is_deleted = models.BooleanField("Deleted", default=False)

    created_at = models.DateTimeField("Created", db_index=True, default=timezone.now)
    updated_at = models.DateTimeField("Changed", auto_now=True)

    objects = BaseQuerySet.as_manager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs) -> None:
        # Переписал условие под уже существующий флаговый аттрибут. Не понимаю, зачем нам ещё один.
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
    due_months = models.IntegerField("Due months", blank=True, null=True)

    def __str__(self):
        return self.code

    @property
    def compliance(self) -> object | None:
        try:
            return self.compliances.latest("perform_date")
        except CW.DoesNotExist:
            return None


class CW(BaseModel):
    task = models.ForeignKey("Task", on_delete=models.CASCADE, related_name="compliances")
    perform_date = models.DateField("Perform date")
    next_due_date = models.DateField("Next due date", blank=True, null=True)

    class Meta:
        unique_together = ("task", "perform_date")
        constraints = [
            models.CheckConstraint(
                name="perform_date_lte_today",
                check=Q(perform_date__lte=timezone.now().date())
            )
        ]

    def __str__(self):
        return f"CW for task: {self.task}"
