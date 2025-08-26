from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Course


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "teacher", "is_active", "created_at")
    list_filter = ("is_active", "created_at", "teacher__role")
    search_fields = ("title", "description", "teacher__email")
    ordering = ("-created_at",)
    filter_horizontal = ("students", "teachers")

    fieldsets = (
        (_("Basic Information"), {"fields": ("title", "description", "teacher")}),
        (_("Enrollment"), {"fields": ("students", "teachers")}),
        (_("Status"), {"fields": ("is_active",)}),
    )

    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user.is_superuser or obj.teacher == request.user

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user.is_superuser or obj.teacher == request.user
