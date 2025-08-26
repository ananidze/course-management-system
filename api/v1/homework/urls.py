from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HomeworkViewSet

homework_router = DefaultRouter(trailing_slash=False)
homework_router.register(r"", HomeworkViewSet, basename="homework")

app_name = "homework"

urlpatterns = [
    path("", include(homework_router.urls)),
]
