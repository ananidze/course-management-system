from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Homework, HomeworkSubmission, Grade


@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ("title", "lecture", "due_date", "is_active", "created_at")
    list_filter = ("is_active", "created_at", "lecture__course")
    search_fields = ("title", "description", "lecture__topic")
    ordering = ("-created_at",)

    fieldsets = (
        (_("Basic Information"), {"fields": ("lecture", "title", "description")}),
        (_("Settings"), {"fields": ("due_date", "max_points", "is_active")}),
    )

    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user.is_superuser or obj.lecture.course.is_teacher(request.user)

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user.is_superuser or obj.lecture.course.is_teacher(request.user)


@admin.register(HomeworkSubmission)
class HomeworkSubmissionAdmin(admin.ModelAdmin):
    list_display = ("student", "homework", "submitted_at")
    list_filter = ("submitted_at", "homework__lecture__course")
    search_fields = ("student__email", "homework__title")
    ordering = ("-submitted_at",)

    fieldsets = (
        (_("Submission"), {"fields": ("homework", "student", "content", "attachment")}),
    )

    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user.is_superuser or obj.homework.lecture.course.is_teacher(request.user)

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user.is_superuser or obj.homework.lecture.course.is_teacher(request.user)


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("submission", "grade", "graded_by", "graded_at")
    list_filter = ("graded_at", "graded_by__role")
    search_fields = ("submission__student__email", "submission__homework__title")
    ordering = ("-graded_at",)

    fieldsets = (
        (_("Grade Information"), {"fields": ("submission", "grade", "comments", "graded_by")}),
    )

    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user.is_superuser or obj.graded_by == request.user

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user.is_superuser or obj.graded_by == request.user
