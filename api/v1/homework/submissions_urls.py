from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HomeworkSubmissionViewSet

submissions_router = DefaultRouter(trailing_slash=False)
submissions_router.register(r"", HomeworkSubmissionViewSet, basename="submission")

app_name = "submissions"

urlpatterns = [
    path("", include(submissions_router.urls)),
]
