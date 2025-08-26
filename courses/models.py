from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class Course(models.Model):
    title = models.CharField(max_length=200, help_text="Course title", db_index=True)
    description = models.TextField(help_text="Course description")
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_courses",
        help_text="Primary teacher of the course",
        db_index=True,
    )

    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="enrolled_courses",
        blank=True,
        help_text="Students enrolled in this course",
    )

    teachers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="teaching_courses",
        blank=True,
        help_text="Additional teachers for this course",
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether the course is active", db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "courses"
        verbose_name = "Course"
        verbose_name_plural = "Courses"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["teacher", "is_active"]),
            models.Index(fields=["created_at", "is_active"]),
            models.Index(fields=["title"]),
            models.Index(fields=["teacher", "created_at"]),
            models.Index(fields=["is_active", "created_at"]),
        ]

    def __str__(self):
        return self.title

    @property
    def total_students(self):
        return self.students.count()

    @property
    def total_teachers(self):
        return self.teachers.count()

    @property
    def total_lectures(self):
        return self.lectures.count()

    @property
    def total_homework_assignments(self):
        return sum(
            lecture.homework_assignments.count() for lecture in self.lectures.all()
        )

    def is_enrolled_student(self, user):
        return user in self.students.all()

    def is_teacher(self, user):
        return user == self.teacher or user in self.teachers.all()

    def can_access(self, user):
        return self.is_teacher(user) or self.is_enrolled_student(user)

    def add_student(self, user):
        if not user.is_student:
            raise ValidationError(_("Only students can be enrolled in courses."))
        if user in self.students.all():
            raise ValidationError(_("Student is already enrolled in this course."))
        self.students.add(user)

    def remove_student(self, user):
        if user in self.students.all():
            self.students.remove(user)

    def add_teacher(self, user):
        if not user.is_teacher:
            raise ValidationError(_("Only teachers can be added to courses."))
        if user in self.teachers.all():
            raise ValidationError(_("Teacher is already assigned to this course."))
        self.teachers.add(user)

    def remove_teacher(self, user):
        if user in self.teachers.all():
            self.teachers.remove(user)
