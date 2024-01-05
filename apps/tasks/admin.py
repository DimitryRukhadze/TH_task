from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

from .models import CW, Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("code", "task_description", "latest_compliance", "is_deleted")
    list_filter = ("is_deleted",)
    search_fields = ("code",)
    ordering = ["code"]

    def task_description(self, obj):
        return obj.description[:50]

    def latest_compliance(self, obj):
        compliance = obj.compliance

        if not compliance:
            return None

        url = (
            reverse("admin:tasks_cw_change", args=f"{compliance.id}")
            + "?"
            + urlencode({"tasks__id": f"{obj.id}"})
        )
        return format_html("<a href=\"{}\">{}</a>", url, f"{compliance.perform_date}")


    latest_compliance.short_description = "Последнее CW"
    task_description.short_description = "Описание"


@admin.register(CW)
class CWAdmin(admin.ModelAdmin):
    list_display = ("related_task", "perform_date", "next_due_date", "is_deleted")
    list_filter = ("is_deleted",)
    search_fields = ("task", )
    ordering = ["-perform_date"]

    def related_task(self, obj):
        return obj

    related_task.short_description = "CW"
