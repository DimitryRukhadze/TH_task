from django.contrib import admin
from .models import Task, CW


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_filter = ("is_deleted",)
    search_fields = ("code__startswith",)


@admin.register(CW)
class CWAdmin(admin.ModelAdmin):
    list_filter = ("is_deleted",)
    search_fields = ("perform_date", "next_due_date")
