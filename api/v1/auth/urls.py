from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    user_registration,
    user_login,
    user_logout,
    get_current_user,
)

app_name = "auth"

urlpatterns = [
    path("me", get_current_user, name="current-user"),
    path("sign-in", user_login, name="user-login"),
    path("sign-up", user_registration, name="user-registration"),
    path("sign-out", user_logout, name="user-logout"),
    path("refresh", TokenRefreshView.as_view(), name="token-refresh"),
]
