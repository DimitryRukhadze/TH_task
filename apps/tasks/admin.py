from django.contrib import admin
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.html import format_html

from .models import Task, CW, Requirements


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
            'code',
            'task_description',
            'latest_cw',
            'active_requirements',
            'is_deleted'
        )
    list_filter = ("is_deleted",)
    search_fields = ("code",)
    ordering = ['code']

    def task_description(self, obj):
        return obj.description[:50]

    def latest_cw(self, obj):
        cw = obj.compliance

        if not cw:
            return None

        url = (
            reverse('admin:tasks_cw_change', args=(cw.pk, ))
            + '?'
            + urlencode({'tasks__id': f'{obj.pk}'})
        )
        return format_html('<a href="{}">{}</a>', url, cw)

    latest_cw.short_description = 'Последнее CW'
    task_description.short_description = 'Описание'

    def active_requirements(self, obj):
        active_requirements = obj.curr_requirements

        if not active_requirements:
            return None

        url = (
            reverse(
                    "admin:tasks_requirements_change",
                    args=(active_requirements.pk, )
                )
            + "?"
            + urlencode({"tasks__id": f"{obj.pk}"})
        )
        return format_html("<a href='{}'>{}</a>", url, active_requirements)


@admin.register(CW)
class CWAdmin(admin.ModelAdmin):
    list_display = (
        "related_task",
        "perform_date",
        "next_due_date",
        "adjusted_days",
        "perform_hours",
        "next_due_hrs",
        "adjusted_hrs",
        "perform_cycles",
        "next_due_cycles",
        "adjusted_cycles",
        "is_deleted"
        )
    list_filter = ("is_deleted",)
    search_fields = ("task", )
    ordering = ['-perform_date']

    def related_task(self, obj):
        return obj

    related_task.short_description = 'CW'


@admin.register(Requirements)
class RequirementsAdmin(admin.ModelAdmin):
    list_display = (
        "related_task",
        "pos_tol_mos",
        "neg_tol_mos",
        "mos_unit",
        "pos_tol_hrs",
        "neg_tol_hrs",
        "hrs_unit",
        "pos_tol_afl",
        "neg_tol_afl",
        "afl_unit",
        "is_active",
        "is_deleted"
    )

    search_fields = ("task", )
    ordering = ["task"]

    def related_task(self, obj):
        return obj

    related_task.short_description = 'requirements'
