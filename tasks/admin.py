from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from tasks.models import Worker, Position, TaskType, Task

admin.site.unregister(Group)


@admin.register(Worker)
class WorkerAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ("position",)
    fieldsets = UserAdmin.fieldsets + (
        ("Additional info", {"fields": ("position",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Additional info",
            {
                "fields": ("first_name", "last_name", "position",),
            },
        ),
    )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "name", "task_type", "priority", "deadline", "is_completed",
    )
    search_fields = ("name",)
    list_filter = (
        "assignees", "task_type", "deadline", "is_completed", "priority",
    )


admin.site.register(Position)
admin.site.register(TaskType)
