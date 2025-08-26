from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LectureViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r"", LectureViewSet, basename="lecture")

app_name = "lectures"

urlpatterns = [
    path("", include(router.urls)),
]
