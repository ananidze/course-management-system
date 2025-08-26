from django.db import models
from courses.models import Course


class Lecture(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lectures",
        help_text="Course this lecture belongs to",
        db_index=True,
    )
    topic = models.CharField(max_length=200, help_text="Lecture topic", db_index=True)
    description = models.TextField(blank=True, help_text="Lecture description")
    presentation_file = models.FileField(
        upload_to="presentations/",
        blank=True,
        null=True,
        help_text="Presentation file (PDF, PPT, etc.)",
    )
    is_published = models.BooleanField(
        default=False,
        help_text="Whether the lecture is published to students",
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "lectures"
        verbose_name = "Lecture"
        verbose_name_plural = "Lectures"
        ordering = ["course", "created_at"]
        indexes = [
            models.Index(fields=["course", "is_published"]),
            models.Index(fields=["is_published", "created_at"]),
            models.Index(fields=["course", "created_at"]),
            models.Index(fields=["topic"]),
            models.Index(fields=["course", "is_published", "created_at"]),
        ]

    def __str__(self):
        return f"{self.course.title} - {self.topic}"

    def can_access(self, user):
        return self.course.can_access(user)

    @property
    def has_presentation(self):
        return bool(self.presentation_file)

    @property
    def total_homework_assignments(self):
        return self.homework_assignments.count()
