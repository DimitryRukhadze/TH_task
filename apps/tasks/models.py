from django.db import models
from django.db.models import Q, QuerySet
from django.utils import timezone


# Для поддержания единого читаемого стиля в админке:
# 1) всем полям лучше определить verbose_name 
# 2) также стоит задать verbose_name для модели
# 3) Также стоит переопределить метод __str__


# Напомню, в ТЗ указано, что должно быть реализовано мягкое удаление
# Лучшим вариантом будет сделать для этого абстрактную модель
class BaseQuerySet(models.query.QuerySet):
    def active(self: QuerySet) -> QuerySet:
        return self.filter(is_deleted=False)


class BaseModel(models.Model):
    is_deleted = models.BooleanField("Deleted", default=False)

    # очень полезные поля, ими не стоит принебрегать
    created_at = models.DateTimeField(db_index=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = BaseQuerySet.as_manager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs) -> None:
        if self._state.adding and hasattr(self, "is_active"):
            self.is_active = True

        return super().save(*args, **kwargs)

    def delete(self):
        self.is_deleted = True
        self.save()


class Task(BaseModel):
    # Зачем нужно явное объявление поля id? По-умолчанию Django нам итак сделает первичный ключ. 
    # https://docs.djangoproject.com/en/5.0/topics/db/models/#automatic-primary-key-fields
    # Это было бы обосновано, например, если бы мы хотели изменить тип ключа скажем на UUID.
    id = models.BigAutoField(primary_key=True, editable=False)

    # поле code - есть идентификатор таска, если ты посмотришь в отчет из CAMP, то ты увидишь, что
    # code может быть текстовым. Уместно переделать в CharField
    code = models.IntegerField()

    description = models.TextField()

    # Ты невнимательно прочел ТЗ, которое я написал:
    # "Задача МОЖЕТ иметь установленную периодичность выполнения в месяцах"
    due_months = models.IntegerField()


class CW(BaseModel):
    # очевидно мы будем создавать связанные QuerySet, 
    # поэтому внешнему ключу стоит установить related_name
    task = models.ForeignKey('Task', on_delete=models.CASCADE)

    # лучше переименовать данное поле в date_performed (или perform_date), 
    # в противном случае не видя модели,
    # можно предположить, что поле BoolenField
    performed = models.DateField()

    # а если мы не можем посчитать next_due_date - если у таска нет заданного интервала
    next_due_date = models.DateField()

    # потерял поле remaining_days!
