from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


class CustomUserAdmin(UserAdmin):
    """Custom admin for the User model."""

    list_display = (
        "email",
        "get_full_name",
        "role",
        "gender",
        "is_active",
        "date_joined",
    )
    list_filter = ("role", "gender", "is_active", "date_joined")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("-date_joined",)

    # Override filter_horizontal to remove references to non-existent fields
    filter_horizontal = ()

    # Fieldsets for the add form
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "role", "gender"),
            },
        ),
    )

    # Fieldsets for the change form
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "gender")}),
        (
            _("Permissions"),
            {
                "fields": ("role", "is_active", "is_staff", "is_superuser"),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    readonly_fields = ("last_login", "date_joined")

    def get_full_name(self, obj):
        return obj.get_full_name()

    get_full_name.short_description = _("Full Name")


admin.site.register(User, CustomUserAdmin)
