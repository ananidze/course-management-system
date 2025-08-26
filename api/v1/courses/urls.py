from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import CourseViewSet, CourseLectureViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r"", CourseViewSet, basename="course")

# Create nested router for lectures
nested_router = routers.NestedDefaultRouter(router, r"", lookup="course")
nested_router.register(r"lectures", CourseLectureViewSet, basename="course-lectures")

app_name = "courses"

urlpatterns = [
    path("", include(router.urls)),
    path("", include(nested_router.urls)),
]
