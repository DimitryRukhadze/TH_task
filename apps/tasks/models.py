from django.db import models
from django.db.models import QuerySet
from django.utils import timezone


class BaseQuerySet(QuerySet):
    def active(self: QuerySet) -> QuerySet:
        return self.filter(is_deleted=False)


class BaseModel(models.Model):
    is_deleted = models.BooleanField("Deleted", default=False)

    created_at = models.DateTimeField(db_index=True, verbose_name="Создано", default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Изменено")

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


class Task(BaseModel):
    # Максимальную длину указал исходя из самого длинного кода с запасом +10 символов
    code = models.CharField(max_length=250, verbose_name='Код задачи')
    description = models.TextField(verbose_name='Описание')
    due_months = models.IntegerField(blank=True, null=True, verbose_name='Месяцев до повтора задачи')

    def __str__(self):
        return self.code

    @property
    def get_latest_cw(self):
        active_cws = self.complied_with.active()
        if not active_cws:
            return 'No active cws'
        return active_cws.latest('perform_date')



class CW(BaseModel):
    task = models.ForeignKey('Task', on_delete=models.CASCADE, related_name='complied_with')
    perform_date = models.DateField(verbose_name='Была выполнена')
    next_due_date = models.DateField(blank=True, null= True, verbose_name='Следующее выполнение')

    def __str__(self):
        return f'{self.task}'
