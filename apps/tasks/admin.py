from django.contrib import admin
from .models import Task, CW


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('code', 'task_description', 'latest_cw', 'is_deleted')
    list_filter = ("is_deleted",)
    search_fields = ("code",)
    ordering = ['code']

    def task_description(self, obj):
        return obj.description[:50]

    def latest_cw(self, obj):
        return obj.get_latest_cw

    latest_cw.short_description = 'Последнее CW'
    task_description.short_description = 'Описание'


@admin.register(CW)
class CWAdmin(admin.ModelAdmin):
    list_display = ("task", "perform_date", "next_due_date", "is_deleted")
    list_filter = ("is_deleted",)
    search_fields = ("task", )
    ordering = ['-perform_date']
