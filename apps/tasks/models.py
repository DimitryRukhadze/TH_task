from django.db import models


class Task(models.Model):
    id = models.BigAutoField(primary_key=True, editable=False)
    code = models.IntegerField()
    description = models.TextField()
    due_months = models.IntegerField()


class CW(models.Model):
    task = models.ForeignKey('Task', on_delete=models.CASCADE)
    performed = models.DateField()
    next_due_date = models.DateField()
