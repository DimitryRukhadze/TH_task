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
    code = models.CharField(max_length=50, verbose_name='Код задачи')
    description = models.TextField(verbose_name='Описание')
    due_months = models.IntegerField(blank=True, verbose_name='Месяцев до повтора задачи')

    def __str__(self):
        return f'{self.code}, {self.description}, {self.complied_with.all()}'


class CW(BaseModel):
    # Это поле мне кажется лишним, т.к. получается, что у одной CW может быть несколько задач. Разве не должно быть наоборот?
    task = models.ForeignKey('Task', on_delete=models.CASCADE, related_name='complied_with')
    perform_date = models.DateField(verbose_name='Была выполнена')
    next_due_date = models.DateField(verbose_name='Следующее выполнение')

    def __str__(self):
        tasks = ', '.join(task.code for task in self.task.all())
        return f'Tasks: {tasks}\n perfomed at: {self.perform_date}\n next_due_date: {self.next_due_date}'
