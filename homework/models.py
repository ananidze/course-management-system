from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from lectures.models import Lecture
from django.utils import timezone


class Homework(models.Model):
    lecture = models.ForeignKey(
        Lecture,
        on_delete=models.CASCADE,
        related_name="homework_assignments",
        help_text="Lecture this homework belongs to",
        db_index=True,
    )
    title = models.CharField(max_length=200, help_text="Homework title", db_index=True)
    description = models.TextField(help_text="Homework description")
    due_date = models.DateTimeField(
        help_text="Due date for homework submission", db_index=True
    )
    max_points = models.PositiveIntegerField(
        default=100,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Maximum points for this homework",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the homework is active and accepting submissions",
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "homework"
        verbose_name = "Homework"
        verbose_name_plural = "Homework"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["lecture", "is_active"]),
            models.Index(fields=["due_date", "is_active"]),
            models.Index(fields=["created_at", "is_active"]),
        ]

    def __str__(self):
        return f"{self.lecture.topic} - {self.title}"

    @property
    def is_overdue(self):
        return timezone.now() > self.due_date

    @property
    def total_submissions(self):
        return self.submissions.count()

    @property
    def graded_submissions(self):
        return self.submissions.filter(grade__isnull=False).count()

    @property
    def average_grade(self):
        grades = self.submissions.filter(grade__isnull=False).values_list(
            "grade__grade", flat=True
        )
        if grades:
            return sum(grades) / len(grades)
        return 0

    def can_submit(self, user):
        if not self.is_active:
            return False
        if self.is_overdue:
            return False
        return self.lecture.course.is_enrolled_student(user)

    def get_student_submission(self, user):
        try:
            return self.submissions.get(student=user)
        except HomeworkSubmission.DoesNotExist:
            return None

    def get_submission_status(self, user):
        submission = self.get_student_submission(user)
        if not submission:
            return "not_submitted"
        if submission.is_late:
            return "late"
        if submission.grade:
            return "graded"
        return "submitted"


class HomeworkSubmission(models.Model):
    homework = models.ForeignKey(
        Homework,
        on_delete=models.CASCADE,
        related_name="submissions",
        help_text="Homework this submission is for",
        db_index=True,
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="homework_submissions",
        help_text="Student who submitted the homework",
        db_index=True,
    )
    content = models.TextField(help_text="Homework submission content")
    attachment = models.FileField(
        upload_to="homework_submissions/",
        blank=True,
        null=True,
        help_text="Optional attachment file",
    )
    submitted_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "homework_submissions"
        verbose_name = "Homework Submission"
        verbose_name_plural = "Homework Submissions"
        ordering = ["-submitted_at"]
        unique_together = ["homework", "student"]
        indexes = [
            models.Index(fields=["homework", "student"]),
            models.Index(fields=["student", "submitted_at"]),
            models.Index(fields=["submitted_at"]),
        ]

    def __str__(self):
        return f"{self.student.get_full_name} - {self.homework.title}"

    @property
    def is_late(self):
        return self.submitted_at > self.homework.due_date

    @property
    def grade_value(self):
        return self.grade.grade if hasattr(self, "grade") else None

    @property
    def letter_grade(self):
        if hasattr(self, "grade"):
            return self.grade.letter_grade
        return None


class Grade(models.Model):
    submission = models.OneToOneField(
        HomeworkSubmission,
        on_delete=models.CASCADE,
        related_name="grade",
        help_text="Homework submission being graded",
        db_index=True,
    )
    grade = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Grade (0-100)",
    )
    comments = models.TextField(
        blank=True, help_text="Teacher comments on the submission"
    )
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="grades_given",
        help_text="Teacher who graded the submission",
        db_index=True,
    )
    graded_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "grades"
        verbose_name = "Grade"
        verbose_name_plural = "Grades"
        ordering = ["-graded_at"]
        indexes = [
            models.Index(fields=["submission"]),
            models.Index(fields=["graded_by", "graded_at"]),
            models.Index(fields=["graded_at"]),
        ]

    def __str__(self):
        return f"Grade {self.grade} for {self.submission.student.get_full_name}"

    @property
    def percentage(self):
        return f"{self.grade}%"

    @property
    def letter_grade(self):
        if self.grade >= 90:
            return "A"
        elif self.grade >= 80:
            return "B"
        elif self.grade >= 70:
            return "C"
        elif self.grade >= 60:
            return "D"
        else:
            return "F"
