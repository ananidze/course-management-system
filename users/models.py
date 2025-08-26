from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from users.managers import BaseUserManager


class User(AbstractUser):
    class Role(models.TextChoices):
        TEACHER = "teacher", _("Teacher")
        STUDENT = "student", _("Student")

    class Gender(models.TextChoices):
        MALE = "male", _("Male")
        FEMALE = "female", _("Female")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = BaseUserManager()

    username = None
    email = models.EmailField(
        unique=True,
        verbose_name=_("Email address"),
        db_index=True,
    )

    first_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name=_("First name"),
    )

    last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name=_("Last name"),
    )

    role = models.CharField(
        choices=Role.choices,
        default=Role.STUDENT,
        verbose_name=_("Role"),
        db_index=True,
    )

    gender = models.CharField(
        choices=Gender.choices,
        blank=True,
        verbose_name=_("Gender"),
    )

    class Meta:
        db_table = "users"
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["role"]),
            models.Index(fields=["role", "is_active"]),
            models.Index(fields=["date_joined"]),
        ]

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
