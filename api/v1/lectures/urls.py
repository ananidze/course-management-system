from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import LectureViewSet, LectureHomeworkViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r"", LectureViewSet, basename="lecture")

# Create nested router for homework within lectures
nested_router = routers.NestedDefaultRouter(router, r"", lookup="lecture")
nested_router.register(r"homework", LectureHomeworkViewSet, basename="lecture-homework")

app_name = "lectures"

urlpatterns = [
    path("", include(router.urls)),
    path("", include(nested_router.urls)),
]
