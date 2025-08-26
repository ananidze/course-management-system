from django.urls import path, include

from .views import health_check

urlpatterns = [
    path("health/", health_check, name="health"),
    path("auth/", include("api.v1.auth.urls")),
    path("courses/", include("api.v1.courses.urls")),
    path("lectures/", include("api.v1.lectures.urls")),
    path("homework/", include("api.v1.homework.urls")),
    path("submissions/", include("api.v1.homework.submissions_urls")),
]
