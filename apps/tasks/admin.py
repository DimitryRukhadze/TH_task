from django.contrib import admin
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.html import format_html

from .models import Task, CW, Tolerance


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
            'code',
            'task_description',
            'latest_cw',
            'is_deleted'
        )
    list_filter = ("is_deleted",)
    search_fields = ("code",)
    ordering = ['code']

    def task_description(self, obj):
        return obj.description[:50]

    def latest_cw(self, obj):
        latest_cw = obj.compliance

        if not latest_cw:
            return None

        url = (
            reverse('admin:tasks_cw_change', args=f'{latest_cw.pk}')
            + '?'
            + urlencode({'tasks__id': f'{obj.pk}'})
        )
        return format_html('<a href="{}">{}</a>', url, latest_cw)

    latest_cw.short_description = 'Последнее CW'
    task_description.short_description = 'Описание'


@admin.register(CW)
class CWAdmin(admin.ModelAdmin):
    list_display = (
        "related_task",
        "perform_date",
        "next_due_date",
        "adjusted_days",
        "is_deleted"
        )
    list_filter = ("is_deleted",)
    search_fields = ("task", )
    ordering = ['-perform_date']

    def related_task(self, obj):
        return obj

    related_task.short_description = 'CW'


@admin.register(Tolerance)
class ToleranceAdmin(admin.ModelAdmin):
    list_display = (
        "related_task",
        "pos_tol",
        "neg_tol",
        "tol_type",
        "is_deleted"
    )
    search_fields = ("task", )
    ordering = ["task"]

    def related_task(self, obj):
        return obj

    related_task.short_description = 'Tolerance'
