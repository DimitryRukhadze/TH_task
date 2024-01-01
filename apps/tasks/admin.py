from django.contrib import admin
from .models import Task, CW


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    pass


@admin.register(CW)
class CWAdmin(admin.ModelAdmin):
    pass
