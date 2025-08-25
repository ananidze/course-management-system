from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Lecture


@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = ("topic", "course", "is_published", "created_at")
    list_filter = ("is_published", "created_at", "course")
    search_fields = ("topic", "description", "course__title")
    ordering = ("course", "created_at")

    fieldsets = (
        (_("Basic Information"), {"fields": ("course", "topic", "description")}),
        (_("Content"), {"fields": ("presentation_file",)}),
        (_("Settings"), {"fields": ("is_published",)}),
    )

    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user.is_superuser or obj.course.is_teacher(request.user)

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user.is_superuser or obj.course.is_teacher(request.user)
